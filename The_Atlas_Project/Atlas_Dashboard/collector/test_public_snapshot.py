"""Privacy and project-selection checks for the public AWS snapshot."""

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import public_snapshot


class PublicSnapshotTests(unittest.TestCase):
    def test_only_opted_in_projects_and_safe_fields_are_published(self):
        config = [
            {"id": "public-app", "name": "Public App", "public": True,
             "tagValue": "secret-tag", "regions": ["eu-west-2"],
             "roleArn": "arn:aws:iam::123456789012:role/private", "showCosts": True,
             "showResourceNames": False, "url": "https://example.org/app"},
            {"id": "private-app", "name": "Private App", "public": False,
             "tagValue": "private-tag", "regions": ["eu-west-2"]},
        ]
        aws_result = {
            "monthCost": 12.34, "currency": "USD", "dailyCost": [1.23],
            "monthForecast": 18.75, "forecastCurrency": "USD",
            "forecastCheckedAt": "2026-10-03T12:00:00+00:00",
            "services": [{"name": "Amazon EC2", "cost": 12.34}],
            "invoiceId": "INV-PRIVATE-2026", "paymentMethod": "CARD-PRIVATE",
            "billingAccount": "BILLING-PRIVATE", "taxDetails": "TAX-PRIVATE",
            "traffic": {"visits": 23, "pageViews": 47, "requests": 190,
                        "bytesDownloaded": 2048, "checkedAt": "2026-10-03T12:00:00+00:00",
                        "accountId": "TRAFFIC-PRIVATE"},
            "health": {"availabilityPercent": 99.2, "error5xxPercent": 0.5,
                       "error4xxPercent": 1.3, "checkedAt": "2026-10-03T12:00:00+00:00",
                       "canaryName": "CANARY-PRIVATE"},
            "resources": [{"name": "private-hostname", "arn": "arn:aws:ec2:eu-west-2:123456789012:instance/i-secret",
                           "type": "EC2 instance", "region": "eu-west-2", "status": "running",
                           "cpu": 17.2, "detail": "t3.micro"}],
            "warnings": [], "checkedAt": "2026-10-03T12:00:00+00:00",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "projects.json"
            path.write_text(json.dumps(config))
            with patch.object(public_snapshot, "get_project_data", return_value=aws_result) as reader:
                snapshot = public_snapshot.collect(path)
        self.assertEqual(reader.call_count, 1)
        self.assertEqual(len(snapshot["projects"]), 1)
        project = snapshot["projects"][0]
        self.assertEqual(project["monthCost"], 12.34)
        self.assertEqual(project["monthForecast"], 18.75)
        self.assertEqual(project["health"]["availabilityPercent"], 99.2)
        self.assertEqual(project["resources"][0]["name"], "EC2 instance 1")
        self.assertEqual(project["url"], "https://example.org/app")
        self.assertEqual(project["traffic"]["visits"], 23)
        self.assertEqual(project["traffic"]["requests"], 190)
        encoded = json.dumps(snapshot)
        for secret in ("secret-tag", "private-tag", "private-hostname", "123456789012", "i-secret", "Private App",
                       "INV-PRIVATE-2026", "CARD-PRIVATE", "BILLING-PRIVATE", "TAX-PRIVATE", "TRAFFIC-PRIVATE", "CANARY-PRIVATE"):
            self.assertNotIn(secret, encoded)

    def test_project_link_requires_https(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "projects.json"
            path.write_text(json.dumps([{"id": "app", "name": "App", "public": True,
                                         "tagValue": "app", "regions": ["eu-west-2"],
                                         "url": "javascript:alert(1)"}]))
            with self.assertRaises(ValueError):
                public_snapshot.configured_projects(path)

    def test_cost_forecast_is_hidden_when_costs_are_not_public(self):
        item = {"id": "app", "name": "App", "showCosts": False}
        data = {"monthCost": 12.5, "monthForecast": 18.9,
                "forecastCurrency": "USD", "services": [{"name": "Amazon S3", "cost": 12.5}]}
        published = public_snapshot.public_project(item, data)
        self.assertIsNone(published["monthCost"])
        self.assertIsNone(published["monthForecast"])
        self.assertEqual(published["services"], [])

    def test_atlas_website_without_cost_data_cannot_publish_costs(self):
        config = Path(__file__).resolve().parent / "public_projects.json"
        current = {"monthCost": 0, "monthForecast": 0,
                   "services": [{"name": "Amazon CloudFront", "cost": 0}],
                   "resources": [], "warnings": [], "checkedAt": datetime.now(timezone.utc).isoformat()}
        with patch.object(public_snapshot, "get_project_data", return_value=current) as reader:
            snapshot = public_snapshot.collect(config)
        reader.assert_called_once()
        self.assertFalse(reader.call_args.kwargs["include_costs"])
        website = snapshot["projects"][0]
        self.assertEqual(website["name"], "Atlas website")
        self.assertIsNone(website["monthCost"])
        self.assertIsNone(website["monthForecast"])
        self.assertEqual(website["services"], [])
        self.assertNotIn("E6NQ1IKHRLQM1", json.dumps(snapshot))
        self.assertNotIn('"Atlas"', json.dumps(snapshot))

    def test_recent_cost_is_reused_while_compute_refreshes(self):
        now = datetime.now(timezone.utc).isoformat()
        previous = {"projects": [{"id": "app", "monthCost": 42.5,
                                  "costCheckedAt": now, "currency": "USD",
                                  "dailyCost": [42.5], "services": [{"name": "Amazon EC2", "cost": 42.5}],
                                  "monthForecast": 51.2, "forecastCurrency": "USD", "forecastCheckedAt": now}]}
        current = {"monthCost": None, "currency": "USD", "dailyCost": [], "services": [],
                   "resources": [{"name": "hidden", "type": "EC2 instance", "region": "eu-west-2",
                                  "status": "running", "cpu": 34.7, "detail": "t3.micro"}],
                   "warnings": [], "checkedAt": now}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "projects.json"
            path.write_text(json.dumps([{"id": "app", "name": "App", "public": True,
                                         "tagValue": "app", "regions": ["eu-west-2"],
                                         "showCosts": True, "showResourceNames": False}]))
            with patch.object(public_snapshot, "get_project_data", return_value=current) as reader:
                snapshot = public_snapshot.collect(path, previous=previous)
        reader.assert_called_once()
        self.assertFalse(reader.call_args.kwargs["include_costs"])
        project = snapshot["projects"][0]
        self.assertEqual(project["monthCost"], 42.5)
        self.assertEqual(project["monthForecast"], 51.2)
        self.assertEqual(project["resources"][0]["cpu"], 34.7)
        self.assertEqual(project["resources"][0]["name"], "EC2 instance 1")


if __name__ == "__main__":
    unittest.main()
