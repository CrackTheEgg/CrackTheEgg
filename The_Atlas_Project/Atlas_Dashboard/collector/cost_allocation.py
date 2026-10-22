"""Reconcile configured DNS allocations with actual Cost Explorer expenditure."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path


CONFIG_FILE = Path(__file__).resolve().parent / "cost_allocation.json"


def money(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def config(path: Path = CONFIG_FILE) -> dict:
    data = json.loads(path.read_text())
    if data.get("currency") != "USD" or not isinstance(data.get("projects"), list):
        raise ValueError("DNS allocations require a USD project list")
    seen = set()
    for row in data["projects"]:
        if row.get("id") in seen or not row.get("id") or not row.get("domain"):
            raise ValueError("DNS allocations need unique project IDs and domains")
        seen.add(row["id"])
        if money(row.get("monthlyCost")) < 0:
            raise ValueError("DNS allocations cannot be negative")
    return data


def project_cost(direct: float | None, allocation: dict | None) -> dict:
    allocated = float(money(allocation["monthlyCost"])) if allocation else None
    return {
        "directAwsCost": direct,
        "allocatedDnsCost": allocated,
        "combinedOperatingCost": float(money(direct) + money(allocated)) if direct is not None and allocated is not None else None,
        "allocationMethod": "Manual public hosted-zone allocation" if allocation else None,
    }


def reconcile(account: dict | None, projects: list[dict], allocations: dict) -> dict:
    """Manual DNS amounts redistribute the AWS total; they never increase it."""
    rows = allocations["projects"]
    allocated = sum((money(row["monthlyCost"]) for row in rows), Decimal("0"))
    direct_values = [project.get("costAllocation", {}).get("directAwsCost") for project in projects]
    known_direct = [value for value in direct_values if value is not None]
    direct = sum((money(value) for value in known_direct), Decimal("0")) if known_direct else None
    direct_complete = len(known_direct) == len(direct_values) and bool(direct_values)
    actual = account.get("total") if account else None
    hosted = account.get("hostedZoneCost") if account else None
    tax = account.get("tax") if account else None
    one_off = account.get("domainRegistrationCost") if account else None
    residual = (money(actual) - money(tax) - money(one_off) - allocated - (direct or Decimal("0"))
                if all(value is not None for value in (actual, tax, one_off)) else None)
    return {
        "currency": "USD",
        "total": actual,
        "directProjectCost": float(direct) if direct is not None else None,
        "directProjectPartial": not direct_complete,
        "allocatedDnsCost": float(allocated),
        "hostedZoneCost": hosted,
        "dnsDiscrepancy": float(money(hosted) - allocated) if hosted is not None else None,
        "sharedUnallocatedCost": float(residual) if residual is not None else None,
        "sharedIncludesUnattributedProjects": not direct_complete,
        "domainRegistrationCost": one_off,
        "tax": tax,
        "checkedAt": account.get("checkedAt") if account else None,
        "allocationMethod": "Manual public hosted-zone allocation; included in AWS total",
    }
