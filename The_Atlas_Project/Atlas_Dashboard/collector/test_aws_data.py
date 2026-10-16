"""Checks that delivery requests and tracked visits remain distinct."""

import unittest
from unittest.mock import patch

from aws_data import cost_tag_has_usage, get_project_data, health_metrics, month_forecast, traffic_metrics


class FakeCloudWatch:
    def __init__(self):
        self.calls = []

    def get_metric_statistics(self, **request):
        self.calls.append(request)
        averages = {"5xxErrorRate": 0.6, "4xxErrorRate": 1.4,
                    "SuccessPercent": 99.5}
        if request["MetricName"] in averages:
            return {"Datapoints": [{"Average": averages[request["MetricName"]],
                                    "SampleCount": 12}]}
        totals = {"Requests": 190, "BytesDownloaded": 2048,
                  "SessionCount": 23, "PageViewCount": 47}
        return {"Datapoints": [{"Sum": totals[request["MetricName"]]}]}


class FakeSession:
    def __init__(self):
        self.clients = {}

    def client(self, service, region_name):
        assert service == "cloudwatch"
        return self.clients.setdefault(region_name, FakeCloudWatch())


class TrafficMetricsTests(unittest.TestCase):
    def test_cost_tag_requires_exact_value_in_cost_explorer(self):
        class FakeCostExplorer:
            def get_tags(self, **request):
                self.request = request
                return {"Tags": ["Atlas-Other", "Atlas"]}
        class CostSession:
            def __init__(self): self.client_instance = FakeCostExplorer()
            def client(self, service, region_name):
                self.assertion = (service, region_name)
                return self.client_instance
        session = CostSession()
        self.assertTrue(cost_tag_has_usage(session, "Project", "Atlas"))
        self.assertEqual(session.assertion, ("ce", "us-east-1"))
        self.assertEqual(session.client_instance.request["TagKey"], "Project")
        class OtherCostExplorer:
            def get_tags(self, **_request):
                return {"Tags": ["Atlas-Other"]}
        class OtherSession:
            def client(self, *_args, **_kwargs):
                return OtherCostExplorer()
        self.assertFalse(cost_tag_has_usage(OtherSession(), "Project", "Atlas"))

    def test_unavailable_credentials_keep_project_visible_without_fake_readings(self):
        project = {"name": "Atlas website", "regions": ["eu-west-2"],
                   "cloudFrontDistributionId": "EXAMPLE"}
        with patch("aws_data.aws_session", side_effect=RuntimeError("No credentials")):
            data = get_project_data(project)
        self.assertEqual(data["name"], "Atlas website")
        self.assertIsNone(data["monthCost"])
        self.assertIsNone(data["traffic"]["requests"])
        self.assertIsNone(data["health"]["error5xxPercent"])
        self.assertTrue(any("AWS connection unavailable" in message for message in data["warnings"]))

    def test_unconfigured_sources_are_unavailable(self):
        traffic = traffic_metrics(FakeSession(), {"regions": ["eu-west-2"]})
        self.assertIsNone(traffic["visits"])
        self.assertIsNone(traffic["requests"])
        self.assertIsNone(traffic["checkedAt"])

    def test_health_uses_cloudfront_errors_and_canary_success(self):
        session = FakeSession()
        health = health_metrics(session, {"regions": ["eu-west-2"],
                                          "cloudFrontDistributionId": "EXAMPLE",
                                          "syntheticsCanaryName": "atlas-site"})
        self.assertEqual(health["error5xxPercent"], 0.6)
        self.assertEqual(health["error4xxPercent"], 1.4)
        self.assertEqual(health["availabilityPercent"], 99.5)
        cloudfront_call = session.clients["us-east-1"].calls[0]
        self.assertEqual(cloudfront_call["Statistics"], ["Average"])
        self.assertEqual(cloudfront_call["MetricName"], "5xxErrorRate")
        canary_call = session.clients["eu-west-2"].calls[0]
        self.assertEqual(canary_call["Dimensions"], [{"Name": "CanaryName", "Value": "atlas-site"}])

    def test_health_without_sources_does_not_claim_availability(self):
        health = health_metrics(FakeSession(), {"regions": ["eu-west-2"]})
        self.assertIsNone(health["availabilityPercent"])
        self.assertIsNone(health["error5xxPercent"])
        self.assertIsNone(health["checkedAt"])

    def test_forecast_is_tagged_and_labelled_as_full_month(self):
        class FakeCostExplorer:
            def get_cost_forecast(self, **request):
                self.request = request
                return {"Total": {"Amount": "24.678", "Unit": "USD"}}

        class ForecastSession:
            def __init__(self): self.client_instance = FakeCostExplorer()
            def client(self, service, region_name):
                self.assertion = (service, region_name)
                return self.client_instance

        session = ForecastSession()
        forecast = month_forecast(session, "Project", "atlas-site")
        self.assertEqual(forecast["monthForecast"], 24.68)
        self.assertEqual(session.assertion, ("ce", "us-east-1"))
        request = session.client_instance.request
        self.assertEqual(request["Metric"], "UNBLENDED_COST")
        self.assertEqual(request["Filter"], {"Tags": {"Key": "Project", "Values": ["atlas-site"]}})
        self.assertEqual(request["TimePeriod"]["Start"][-2:], "01")

    def test_cloudfront_requests_do_not_become_visits(self):
        session = FakeSession()
        traffic = traffic_metrics(session, {"regions": ["eu-west-2"],
                                            "cloudFrontDistributionId": "EXAMPLE"})
        self.assertEqual(traffic["requests"], 190)
        self.assertEqual(traffic["bytesDownloaded"], 2048)
        self.assertIsNone(traffic["visits"])
        call = session.clients["us-east-1"].calls[0]
        self.assertEqual(call["Dimensions"], [{"Name": "DistributionId", "Value": "EXAMPLE"},
                                               {"Name": "Region", "Value": "Global"}])

    def test_rum_sessions_and_page_views(self):
        session = FakeSession()
        traffic = traffic_metrics(session, {"regions": ["eu-west-2"],
                                            "rumAppMonitor": "atlas-site"})
        self.assertEqual(traffic["visits"], 23)
        self.assertEqual(traffic["pageViews"], 47)
        self.assertIsNone(traffic["requests"])


if __name__ == "__main__":
    unittest.main()
