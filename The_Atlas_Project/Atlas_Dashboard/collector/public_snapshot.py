"""Publish an allowlisted AWS snapshot for the public portfolio dashboard.

Run locally with --output to inspect the exact JSON before publishing. On AWS,
schedule lambda_handler and set ATLAS_PUBLIC_BUCKET to the portfolio bucket.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timedelta, timezone
from math import isfinite
from pathlib import Path
from urllib.parse import urlparse

from aws_data import aws_session, cost_tag_has_usage, get_project_data


BASE = Path(__file__).resolve().parent
PROJECTS_FILE = Path(os.environ.get("ATLAS_PUBLIC_PROJECTS_FILE", BASE / "public_projects.json"))
PUBLIC_KEY = "atlas-dashboard/data/latest.json"


def configured_projects(path: Path = PROJECTS_FILE) -> list[dict]:
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError("Public projects file must contain a list")
    projects = []
    seen = set()
    for item in data:
        if not isinstance(item, dict) or item.get("public") is not True:
            continue
        project_id = item.get("id")
        if not isinstance(project_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", project_id):
            raise ValueError("Public project id must use lowercase letters, digits, and hyphens")
        if project_id in seen:
            raise ValueError("Public project ids must be unique")
        seen.add(project_id)
        if not isinstance(item.get("name"), str) or not item["name"]:
            raise ValueError("Public projects need a name")
        if item.get("tagValue") is not None and (not isinstance(item["tagValue"], str) or not item["tagValue"]):
            raise ValueError("tagValue must be a nonempty string when configured")
        if not isinstance(item.get("costDataReady", True), bool):
            raise ValueError("costDataReady must be a boolean")
        if not isinstance(item.get("previewProtected", False), bool):
            raise ValueError("previewProtected must be a boolean")
        regions = item.get("regions")
        if not isinstance(regions, list) or not regions or not all(isinstance(region, str) and region for region in regions):
            raise ValueError("Public projects need a nonempty regions list")
        role_arn = item.get("roleArn")
        if role_arn is not None and not isinstance(role_arn, str):
            raise ValueError("roleArn must be a string")
        url = item.get("url")
        if url is not None and (not isinstance(url, str) or urlparse(url).scheme != "https" or not urlparse(url).netloc):
            raise ValueError("Public project url must be an HTTPS address")
        for key in ("cloudFrontDistributionId", "rumAppMonitor", "rumRegion",
                    "syntheticsCanaryName", "syntheticsRegion"):
            if item.get(key) is not None and (not isinstance(item[key], str) or not item[key]):
                raise ValueError(f"{key} must be a nonempty string")
        projects.append(item)
    return projects


def public_project(item: dict, data: dict) -> dict:
    """Drop account identifiers, ARNs, tags, and resource IDs before publishing."""
    def safe_number(value, *, maximum=None):
        return value if (isinstance(value, (int, float)) and not isinstance(value, bool)
                         and isfinite(value) and value >= 0
                         and (maximum is None or value <= maximum)) else None

    resources = []
    for index, resource in enumerate(data.get("resources", []), 1):
        resource_type = str(resource.get("type") or "AWS resource")
        resources.append({
            "name": str(resource.get("name") or resource_type) if item.get("showResourceNames") is True else f"{resource_type} {index}",
            "type": resource_type,
            "region": str(resource.get("region") or ""),
            "status": str(resource.get("status") or "tagged"),
            "cpu": resource.get("cpu"),
            "detail": str(resource.get("detail") or "") if resource_type == "EC2 instance" else "",
        })
    show_costs = item.get("showCosts") is True and item.get("costDataReady", True) is True and bool(item.get("tagValue"))
    raw_traffic = data.get("traffic") or {}
    traffic = {key: safe_number(raw_traffic.get(key))
               for key in ("visits", "pageViews", "requests", "bytesDownloaded")}
    traffic["checkedAt"] = raw_traffic.get("checkedAt") if isinstance(raw_traffic.get("checkedAt"), str) else None
    raw_health = data.get("health") or {}
    health = {key: safe_number(raw_health.get(key), maximum=100)
              for key in ("availabilityPercent", "error5xxPercent", "error4xxPercent")}
    health["checkedAt"] = raw_health.get("checkedAt") if isinstance(raw_health.get("checkedAt"), str) else None
    return {
        "id": item["id"],
        "name": item["name"],
        "url": item.get("url"),
        "source": "aws",
        "monthCost": data.get("monthCost") if show_costs else None,
        "monthForecast": safe_number(data.get("monthForecast")) if show_costs else None,
        "forecastCurrency": data.get("forecastCurrency", "USD") if show_costs else "USD",
        "forecastCheckedAt": data.get("forecastCheckedAt") if show_costs else None,
        "costCheckedAt": data.get("costCheckedAt") if show_costs else None,
        "currency": data.get("currency", "USD"),
        "dailyCost": data.get("dailyCost", []) if show_costs else [],
        "services": data.get("services", []) if show_costs else [],
        "resources": resources,
        "traffic": traffic,
        "health": health,
        "warnings": data.get("warnings", []),
        "checkedAt": data.get("checkedAt"),
    }


def collect(path: Path = PROJECTS_FILE, previous: dict | None = None) -> dict:
    projects = configured_projects(path)
    previous_by_id = {item["id"]: item for item in (previous or {}).get("projects", []) if isinstance(item, dict) and isinstance(item.get("id"), str)}
    results = []
    for item in projects:
        try:
            old = previous_by_id.get(item["id"], {})
            cost_time = old.get("costCheckedAt")
            try:
                checked = datetime.fromisoformat(cost_time) if isinstance(cost_time, str) else None
                age = datetime.now(timezone.utc) - checked if checked is not None and checked.tzinfo is not None else None
                cost_recent = age is not None and timedelta(0) <= age < timedelta(hours=24) and checked.strftime("%Y-%m") == datetime.now(timezone.utc).strftime("%Y-%m")
            except ValueError:
                cost_recent = False
            current_month = datetime.now(timezone.utc).strftime("%Y-%m")
            cost_ready = item.get("costDataReady", True) is True
            if item.get("costDataReady") is False and item.get("showCosts") is True and item.get("tagValue"):
                cost_ready = old.get("costReady") is True and old.get("costReadyMonth") == current_month
                probe_time = old.get("costProbeCheckedAt")
                try:
                    probe_checked = datetime.fromisoformat(probe_time) if isinstance(probe_time, str) else None
                    probe_recent = (probe_checked is not None and probe_checked.tzinfo is not None
                                    and timedelta(0) <= datetime.now(timezone.utc) - probe_checked < timedelta(hours=6)
                                    and probe_checked.strftime("%Y-%m") == current_month)
                except ValueError:
                    probe_recent = False
                if not cost_ready and not probe_recent:
                    try:
                        cost_ready = cost_tag_has_usage(
                            aws_session(item), os.environ.get("ATLAS_PROJECT_TAG_KEY", "Project"), item["tagValue"])
                    except Exception:
                        cost_ready = False
                    probe_time = datetime.now(timezone.utc).isoformat()
            else:
                probe_time = None
            effective_item = {**item, "costDataReady": cost_ready}
            costs_configured = item.get("showCosts") is True and cost_ready and bool(item.get("tagValue"))
            reuse_cost = costs_configured and cost_recent and old.get("monthCost") is not None
            data = get_project_data(effective_item, include_costs=costs_configured and not reuse_cost)
            if reuse_cost:
                for field in ("monthCost", "currency", "dailyCost", "services", "costCheckedAt",
                              "monthForecast", "forecastCurrency", "forecastCheckedAt"):
                    data[field] = old.get(field)
            elif item.get("showCosts") is True and data.get("monthCost") is not None:
                data["costCheckedAt"] = datetime.now(timezone.utc).isoformat()
            published = public_project(effective_item, data)
            published["costReady"] = cost_ready
            published["costReadyMonth"] = current_month if cost_ready else None
            published["costProbeCheckedAt"] = probe_time
            results.append(published)
        except Exception:
            results.append({
                "id": item["id"], "name": item["name"], "source": "aws",
                "url": item.get("url"),
                "monthCost": None, "currency": "USD", "dailyCost": [],
                "monthForecast": None, "forecastCurrency": "USD", "forecastCheckedAt": None,
                "costCheckedAt": None,
                "services": [], "resources": [],
                "traffic": {"visits": None, "pageViews": None, "requests": None,
                            "bytesDownloaded": None, "checkedAt": None},
                "health": {"availabilityPercent": None, "error5xxPercent": None,
                           "error4xxPercent": None, "checkedAt": None},
                "warnings": ["AWS data is temporarily unavailable for this project."],
                "checkedAt": datetime.now(timezone.utc).isoformat(),
            })
    return {"schemaVersion": 1, "generatedAt": datetime.now(timezone.utc).isoformat(), "projects": results}


def lambda_handler(event, context):
    bucket = os.environ["ATLAS_PUBLIC_BUCKET"]
    import boto3
    from botocore.exceptions import ClientError
    s3 = boto3.client("s3")
    try:
        previous = json.loads(s3.get_object(Bucket=bucket, Key=PUBLIC_KEY)["Body"].read())
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") not in ("NoSuchKey", "404"):
            raise
        previous = None
    body = json.dumps(collect(previous=previous), separators=(",", ":")).encode("utf-8")
    s3.put_object(
        Bucket=bucket, Key=PUBLIC_KEY, Body=body,
        ContentType="application/json", CacheControl="public, max-age=60",
    )
    return {"projectCount": len(json.loads(body)["projects"]), "key": PUBLIC_KEY}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect a public AWS snapshot before publishing")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--projects", type=Path, default=PROJECTS_FILE)
    args = parser.parse_args()
    args.output.write_text(json.dumps(collect(args.projects), indent=2) + "\n")
    print(f"Wrote {args.output}")
