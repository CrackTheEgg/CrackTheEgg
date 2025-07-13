Project Response – Chapter 01: Lambda Hello World

Prepared By: Solutions Architect (Project Atlas)Date: July 11, 2025

📐 Solution Summary

To fulfill the client’s PoC requirement for a minimal, scalable, serverless compute service, the following solution architecture is proposed.

AWS Lambda for compute

IAM execution role with CloudWatch logging access

Optional API Gateway for HTTP exposure

All components will be deployed manually via the AWS Console to maximize visibility and learning.

🗺️ High-Level Architecture

Components:

Client – manual test via console or API call

API Gateway (optional) – provides public HTTP endpoint

AWS Lambda – core function execution

IAM Role – limited permissions for CloudWatch

Amazon CloudWatch – centralized logging

Flow:

User/Test Event → [API Gateway] → Lambda Function → CloudWatch Logs

🔐 IAM and Security

Execution Role Permissions:

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}

No public storage, no inbound VPC access, no user data.

💻 Deployment Method

AWS Console only

Step-by-step walkthrough to:

Create IAM Role

Deploy Lambda Function

Create test event

View logs in CloudWatch

📊 Observability

Logs captured in Amazon CloudWatch

Metrics auto-enabled (invocation count, duration, errors)

⚙️ Design Considerations

Stateless function design

Event-driven invocation

Free Tier usage

No infrastructure maintenance

✅ Success Metrics

Lambda returns correct output

Logs appear in CloudWatch

IAM permissions function correctly