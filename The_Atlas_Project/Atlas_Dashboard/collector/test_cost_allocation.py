"""Accounting checks for real AWS costs and manual DNS allocations."""

import unittest

from aws_data import account_month_cost, cost_category, month_cost
from cost_allocation import config, project_cost, reconcile


def group(service, usage, amount):
    return {"Keys": [service, usage],
            "Metrics": {"UnblendedCost": {"Amount": str(amount), "Unit": "USD"}}}


class FakeCostExplorer:
    def __init__(self, groups):
        self.groups = groups
        self.requests = []

    def get_cost_and_usage(self, **request):
        self.requests.append(request)
        return {"ResultsByTime": [{"TimePeriod": {"Start": "2026-10-01"},
                                    "Groups": self.groups}]}


class FakeSession:
    def __init__(self, groups):
        self.ce = FakeCostExplorer(groups)

    def client(self, service, region_name):
        assert (service, region_name) == ("ce", "us-east-1")
        return self.ce


class CostAllocationTests(unittest.TestCase):
    def test_october_reference_reconciles_without_dns_double_counting(self):
        session = FakeSession([
            group("Amazon Registrar", "Route53-Domains", "16.00"),
            group("Tax", "NoUsageType", "3.52"),
            group("Amazon Route 53", "HostedZone", "1.50"),
            group("AWS Cost Explorer", "USE1-APIRequest", ".10"),
            group("Amazon Bedrock", "Tokens", ".01"),
            group("Amazon Simple Storage Service", "EUW2-TimedStorage-ByteHrs", ".01"),
        ])
        account = account_month_cost(session)
        self.assertEqual(account["total"], 21.14)
        allocations = config()
        projects = [{"costAllocation": project_cost(None, row)} for row in allocations["projects"]]
        summary = reconcile(account, projects, allocations)
        self.assertEqual([p["costAllocation"]["allocatedDnsCost"] for p in projects], [.50, .50, .50])
        self.assertEqual(summary["allocatedDnsCost"], 1.50)
        self.assertEqual(summary["dnsDiscrepancy"], 0)
        self.assertEqual(summary["total"], 21.14)
        self.assertEqual(summary["sharedUnallocatedCost"], .12)
        self.assertTrue(summary["sharedIncludesUnattributedProjects"])
        self.assertEqual(summary["domainRegistrationCost"], 16)
        self.assertEqual(summary["tax"], 3.52)

    def test_direct_and_manual_costs_do_not_raise_account_total(self):
        allocations = config()
        projects = [{"costAllocation": project_cost(value, row)}
                    for value, row in zip([.01, 0, 0], allocations["projects"])]
        summary = reconcile({"total": 21.14, "hostedZoneCost": 1.50,
                             "domainRegistrationCost": 16, "tax": 3.52,
                             "checkedAt": "2026-10-22T00:00:00+00:00"}, projects, allocations)
        self.assertEqual(projects[0]["costAllocation"]["combinedOperatingCost"], .51)
        self.assertEqual(summary["directProjectCost"], .01)
        self.assertEqual(summary["sharedUnallocatedCost"], .11)
        self.assertEqual(summary["total"], 21.14)

    def test_partial_direct_cost_labels_remaining_balance_as_unattributed(self):
        allocations = config()
        projects = [{"costAllocation": project_cost(value, row)}
                    for value, row in zip([.01, None, None], allocations["projects"])]
        summary = reconcile({"total": 21.14, "hostedZoneCost": 1.50,
                             "domainRegistrationCost": 16, "tax": 3.52}, projects, allocations)
        self.assertEqual(summary["directProjectCost"], .01)
        self.assertTrue(summary["directProjectPartial"])
        self.assertEqual(summary["sharedUnallocatedCost"], .11)
        self.assertTrue(summary["sharedIncludesUnattributedProjects"])

    def test_dns_query_charge_is_not_automatic_hosted_zone_allocation(self):
        session = FakeSession([group("Amazon Route 53", "HostedZone", "1.50"),
                               group("Amazon Route 53", "DNS-Queries", ".20")])
        account = account_month_cost(session)
        self.assertEqual(account["hostedZoneCost"], 1.50)
        self.assertEqual(account["total"], 1.70)
        self.assertEqual(cost_category("Amazon Route 53", "DNS-Queries"), "operating")

    def test_tagged_direct_cost_excludes_hosted_zone_and_one_off_charges(self):
        session = FakeSession([group("Amazon S3", "Storage", ".10"),
                               group("Amazon Route 53", "HostedZone", ".50"),
                               group("Amazon Route 53", "DNSQueries", ".02"),
                               group("Amazon Route 53 Registrar", "DomainRegistration", "16.00")])
        cost = month_cost(session, "Project", "Atlas")
        self.assertEqual(cost["monthCost"], .12)
        self.assertEqual(cost["services"], [{"name": "Amazon S3", "cost": .10},
                                            {"name": "Amazon Route 53", "cost": .02}])
        self.assertEqual(session.ce.requests[0]["Filter"], {"Tags": {"Key": "Project", "Values": ["Atlas"]}})

    def test_hosted_zone_mismatch_is_visible_and_not_forced_to_reconcile(self):
        allocations = config()
        projects = [{"costAllocation": project_cost(0, row)} for row in allocations["projects"]]
        summary = reconcile({"total": 2, "hostedZoneCost": 1.70,
                             "domainRegistrationCost": 0, "tax": 0}, projects, allocations)
        self.assertEqual(summary["dnsDiscrepancy"], .20)
        self.assertEqual(summary["sharedUnallocatedCost"], .50)


if __name__ == "__main__":
    unittest.main()
