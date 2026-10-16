"""Read-only AWS project inventory, traffic metrics, and month-to-date cost."""

from __future__ import annotations

import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from math import isfinite


def aws_session(project: dict):
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError("AWS support needs boto3: pip install -r requirements.txt") from exc
    base = boto3.Session()
    if not project.get("roleArn"):
        return base
    response = base.client("sts").assume_role(RoleArn=project["roleArn"], RoleSessionName="atlas-dashboard-readonly")
    creds = response["Credentials"]
    return boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
    )


def month_cost(session, tag_key: str, tag_value: str) -> dict:
    today = datetime.now(timezone.utc).date()
    ce = session.client("ce", region_name="us-east-1")
    request = {
        "TimePeriod": {"Start": today.replace(day=1).isoformat(), "End": (today + timedelta(days=1)).isoformat()},
        "Granularity": "DAILY",
        "Metrics": ["UnblendedCost"],
        "Filter": {"Tags": {"Key": tag_key, "Values": [tag_value]}},
        "GroupBy": [{"Type": "DIMENSION", "Key": "SERVICE"}],
    }
    by_day = defaultdict(float)
    by_service = defaultdict(float)
    currency = "USD"
    while True:
        response = ce.get_cost_and_usage(**request)
        for day in response.get("ResultsByTime", []):
            date = day["TimePeriod"]["Start"]
            by_day[date] += 0
            for group in day.get("Groups", []):
                metric = group["Metrics"]["UnblendedCost"]
                amount = float(metric["Amount"])
                currency = metric.get("Unit", currency)
                by_day[date] += amount
                by_service[group["Keys"][0]] += amount
        token = response.get("NextPageToken")
        if not token:
            break
        request["NextPageToken"] = token
    services = sorted(({"name": name, "cost": round(value, 2)} for name, value in by_service.items()), key=lambda row: row["cost"], reverse=True)
    return {
        "monthCost": round(sum(by_day.values()), 2),
        "currency": currency,
        "dailyCost": [{"date": day, "cost": round(value, 2)} for day, value in sorted(by_day.items())],
        "services": services,
    }


def month_forecast(session, tag_key: str, tag_value: str) -> dict:
    """Ask Cost Explorer for the current month's tagged unblended-cost estimate."""
    today = datetime.now(timezone.utc).date()
    month_start = today.replace(day=1)
    next_month = (month_start + timedelta(days=32)).replace(day=1)
    response = session.client("ce", region_name="us-east-1").get_cost_forecast(
        TimePeriod={"Start": month_start.isoformat(), "End": next_month.isoformat()},
        Metric="UNBLENDED_COST", Granularity="MONTHLY",
        Filter={"Tags": {"Key": tag_key, "Values": [tag_value]}},
    )
    total = response.get("Total") or {}
    amount = float(total["Amount"])
    if not isfinite(amount) or amount < 0:
        raise ValueError("Cost Explorer returned an invalid forecast")
    return {"monthForecast": round(amount, 2),
            "forecastCurrency": total.get("Unit", "USD"),
            "forecastCheckedAt": datetime.now(timezone.utc).isoformat()}


def health_metrics(session, project: dict) -> dict:
    """Read the last 24 hours of CloudFront errors and optional canary success."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=24)
    health = {"availabilityPercent": None, "error5xxPercent": None,
              "error4xxPercent": None, "checkedAt": None}

    def average(client, namespace: str, name: str, dimensions: list[dict]) -> float | None:
        points = client.get_metric_statistics(
            Namespace=namespace, MetricName=name, Dimensions=dimensions,
            StartTime=start, EndTime=now, Period=3600, Statistics=["Average"],
        ).get("Datapoints", [])
        values = [(float(point["Average"]), float(point.get("SampleCount", 1)))
                  for point in points if "Average" in point]
        if not values:
            return None
        weight = sum(count for _, count in values)
        return round(sum(value * count for value, count in values) / weight, 2) if weight else None

    distribution = project.get("cloudFrontDistributionId")
    if distribution:
        cloudwatch = session.client("cloudwatch", region_name="us-east-1")
        dimensions = [{"Name": "DistributionId", "Value": distribution},
                      {"Name": "Region", "Value": "Global"}]
        health["error5xxPercent"] = average(cloudwatch, "AWS/CloudFront", "5xxErrorRate", dimensions)
        health["error4xxPercent"] = average(cloudwatch, "AWS/CloudFront", "4xxErrorRate", dimensions)

    canary = project.get("syntheticsCanaryName")
    if canary:
        region = project.get("syntheticsRegion") or project["regions"][0]
        cloudwatch = session.client("cloudwatch", region_name=region)
        health["availabilityPercent"] = average(
            cloudwatch, "CloudWatchSynthetics", "SuccessPercent",
            [{"Name": "CanaryName", "Value": canary}],
        )

    if any(health[key] is not None for key in ("availabilityPercent", "error5xxPercent", "error4xxPercent")):
        health["checkedAt"] = now.isoformat()
    return health


def traffic_metrics(session, project: dict) -> dict:
    """Read month-to-date CloudFront delivery and optional RUM session metrics."""
    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    traffic = {"visits": None, "pageViews": None, "requests": None,
               "bytesDownloaded": None, "checkedAt": None}

    def total(client, namespace: str, name: str, dimensions: list[dict]) -> int | None:
        points = client.get_metric_statistics(
            Namespace=namespace, MetricName=name, Dimensions=dimensions,
            StartTime=start, EndTime=now, Period=86400, Statistics=["Sum"],
        ).get("Datapoints", [])
        return round(sum(point["Sum"] for point in points)) if points else None

    distribution = project.get("cloudFrontDistributionId")
    if distribution:
        cloudwatch = session.client("cloudwatch", region_name="us-east-1")
        dimensions = [{"Name": "DistributionId", "Value": distribution},
                      {"Name": "Region", "Value": "Global"}]
        traffic["requests"] = total(cloudwatch, "AWS/CloudFront", "Requests", dimensions)
        traffic["bytesDownloaded"] = total(cloudwatch, "AWS/CloudFront", "BytesDownloaded", dimensions)

    monitor = project.get("rumAppMonitor")
    if monitor:
        cloudwatch = session.client("cloudwatch", region_name=project.get("rumRegion") or project["regions"][0])
        dimensions = [{"Name": "application_name", "Value": monitor}]
        traffic["visits"] = total(cloudwatch, "AWS/RUM", "SessionCount", dimensions)
        traffic["pageViews"] = total(cloudwatch, "AWS/RUM", "PageViewCount", dimensions)

    if any(traffic[key] is not None for key in ("visits", "pageViews", "requests", "bytesDownloaded")):
        traffic["checkedAt"] = now.isoformat()
    return traffic


def resource_inventory(session, regions: list[str], tag_key: str, tag_value: str) -> list[dict]:
    resources = []
    for region in regions:
        tagging = session.client("resourcegroupstaggingapi", region_name=region)
        token = None
        while True:
            request = {"TagFilters": [{"Key": tag_key, "Values": [tag_value]}], "ResourcesPerPage": 100}
            if token:
                request["PaginationToken"] = token
            response = tagging.get_resources(**request)
            for item in response.get("ResourceTagMappingList", []):
                arn = item["ResourceARN"]
                tags = {tag["Key"]: tag["Value"] for tag in item.get("Tags", [])}
                segments = arn.split(":", 5)
                service = segments[2] if len(segments) > 2 else "AWS"
                resource_id = segments[-1].split("/")[-1]
                resources.append({
                    "arn": arn,
                    "name": tags.get("Name", resource_id),
                    "type": service.upper() if service in {"ec2", "ecs", "s3"} else service,
                    "region": region,
                    "status": "tagged",
                    "cpu": None,
                    "detail": resource_id,
                })
            token = response.get("PaginationToken")
            if not token:
                break
    return resources


def enrich_ec2(session, resources: list[dict]) -> None:
    by_region = defaultdict(list)
    for resource in resources:
        if resource["type"] == "EC2" and ":instance/" in resource["arn"]:
            by_region[resource["region"]].append(resource)
    for region, items in by_region.items():
        ec2 = session.client("ec2", region_name=region)
        cloudwatch = session.client("cloudwatch", region_name=region)
        ids = [item["arn"].split("/")[-1] for item in items]
        descriptions = ec2.describe_instances(InstanceIds=ids)
        instances = {instance["InstanceId"]: instance for reservation in descriptions.get("Reservations", []) for instance in reservation.get("Instances", [])}
        for resource in items:
            instance_id = resource["arn"].split("/")[-1]
            instance = instances.get(instance_id)
            if not instance:
                continue
            resource["type"] = "EC2 instance"
            resource["status"] = instance["State"]["Name"]
            resource["detail"] = instance["InstanceType"]
            if resource["status"] != "running":
                continue
            now = datetime.now(timezone.utc)
            points = cloudwatch.get_metric_statistics(
                Namespace="AWS/EC2", MetricName="CPUUtilization",
                Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                StartTime=now - timedelta(hours=2), EndTime=now,
                Period=300, Statistics=["Average"],
            ).get("Datapoints", [])
            if points:
                latest = max(points, key=lambda point: point["Timestamp"])
                resource["cpu"] = round(latest["Average"], 1)


def get_project_data(project: dict, *, include_costs: bool = True) -> dict:
    tag_key = os.environ.get("ATLAS_PROJECT_TAG_KEY", "Project")
    tag_value = project.get("tagValue")
    result = {
        "source": "aws", "name": project["name"], "tagValue": tag_value,
        "regions": project["regions"], "monthCost": None, "currency": "USD",
        "dailyCost": [], "services": [], "resources": [], "warnings": [],
        "monthForecast": None, "forecastCurrency": "USD", "forecastCheckedAt": None,
        "health": {"availabilityPercent": None, "error5xxPercent": None,
                   "error4xxPercent": None, "checkedAt": None},
        "traffic": {"visits": None, "pageViews": None, "requests": None,
                    "bytesDownloaded": None, "checkedAt": None},
        "checkedAt": datetime.now(timezone.utc).isoformat(),
    }
    if tag_value and project.get("costDataReady") is False:
        result["warnings"].append("Cost Explorer has not yet published tagged project costs; totals and forecast are unavailable.")
    if project.get("previewProtected") is True:
        result["warnings"].append("The preview password can raise CloudFront 4xx responses; these are not necessarily app errors.")
    try:
        session = aws_session(project)
    except Exception as exc:
        result["warnings"].append(f"AWS connection unavailable: {type(exc).__name__}. Configure read-only AWS access to load live metrics.")
        if not tag_value:
            result["warnings"].append("Project cost allocation tag is not configured; costs and tagged resources are unavailable.")
        return result
    if project.get("cloudFrontDistributionId") or project.get("rumAppMonitor"):
        try:
            result["traffic"] = traffic_metrics(session, project)
        except Exception as exc:
            result["warnings"].append(f"Traffic data unavailable: {type(exc).__name__}.")
    if project.get("cloudFrontDistributionId") or project.get("syntheticsCanaryName"):
        try:
            result["health"] = health_metrics(session, project)
        except Exception as exc:
            result["warnings"].append(f"Availability or error data unavailable: {type(exc).__name__}.")
    if include_costs and tag_value:
        try:
            result.update(month_cost(session, tag_key, tag_value))
            result["costCheckedAt"] = datetime.now(timezone.utc).isoformat()
        except Exception as exc:
            result["warnings"].append(f"Cost data unavailable: {type(exc).__name__}. Check Cost Explorer access and cost allocation tag activation.")
        try:
            result.update(month_forecast(session, tag_key, tag_value))
        except Exception as exc:
            result["warnings"].append(f"Cost forecast unavailable: {type(exc).__name__}.")
    if not tag_value:
        result["warnings"].append("Project cost allocation tag is not configured; costs and tagged resources are unavailable.")
        return result
    try:
        result["resources"] = resource_inventory(session, project["regions"], tag_key, tag_value)
        try:
            enrich_ec2(session, result["resources"])
        except Exception as exc:
            result["warnings"].append(f"EC2 activity unavailable: {type(exc).__name__}. Check EC2 and CloudWatch read permissions.")
    except Exception as exc:
        result["warnings"].append(f"Resource inventory unavailable: {type(exc).__name__}. Check regions, credentials, and tagging permissions.")
    return result
