# Chapter 3 – Secure Contact Form: Solution Response

## Our Response to the Client Brief

We propose a secure, serverless contact form solution that integrates directly into the existing static website infrastructure while ensuring **no personal data is stored** beyond the time required for message delivery.

The solution builds on the foundational work of:
- **Chapter 1**: Serverless API using AWS Lambda + API Gateway.
- **Chapter 2**: Secure static site hosting with S3 + CloudFront.

By combining these, Chapter 3 demonstrates a **full front–back integration** using AWS best practices.

---

## Architecture Overview

**Key AWS Services:**
- **Amazon S3 + CloudFront** – Hosts the static frontend securely.
- **Amazon API Gateway** – Serves as the secure entry point for form submissions, with domain and CORS restrictions.
- **AWS Lambda** – Processes form data in-memory and triggers the reply workflow.
- **Amazon SES (Simple Email Service)** – Sends thank-you emails.
- **Amazon SNS (Simple Notification Service)** – Sends thank-you SMS messages.
- **Amazon CloudWatch Metrics/Dashboards** – Tracks engagement counts without storing PII.

**Workflow:**
1. User visits the contact form hosted on **CloudFront** (static assets from S3).
2. Form submission POST request goes to **API Gateway**.
3. **API Gateway** triggers **AWS Lambda**.
4. **Lambda** validates input, checks anti-bot mechanisms, sends thank-you message via SES/SNS based on user preference.
5. Engagement type (email, SMS, either) is **counted in CloudWatch Metrics** for reporting.
6. No PII or messages are stored—processing is entirely in-memory.

---

## Why This Architecture

### 1. **Security**
- **No PII stored** – ensures compliance with data protection principles.
- Input validation prevents malicious payloads.
- Anti-bot techniques reduce spam/abuse.
- IAM policies follow **least privilege** – Lambda can only send via SES/SNS and write CloudWatch metrics.

### 2. **Scalability**
- Serverless architecture scales automatically with demand.
- No backend infrastructure to manage.

### 3. **Observability**
- CloudWatch metrics allow us to track usage trends (total engagements, preference counts).
- No need for a database to get actionable reporting.

### 4. **Cost Efficiency**
- Only pay for actual Lambda executions and SES/SNS sends.
- No database or persistent storage means zero ongoing storage costs.

---

## No Data Storage – How It Works

The **core principle** of this design is that no personally identifiable information (PII) is written to persistent storage.

- **Lambda Execution Context**:  
  All form data is handled in-memory during a single Lambda invocation.
- **Transient Processing**:  
  Once SES/SNS sends the message, the contact details are discarded from memory.
- **Logging Hygiene**:  
  CloudWatch logs do **not** include the raw contact details—only metadata such as:
  ```json
  { "hasEmail": true, "hasPhone": false, "replyType": "email" }
  ```
- **Metrics Instead of Storage**:  
  Engagement numbers are stored as CloudWatch metrics, e.g.:
  - `Engagement.Total`
  - `Engagement.ByEmail`
  - `Engagement.BySMS`
  - `Engagement.ByEither`

This ensures **compliance by design**—even if a breach occurred, there is no PII in AWS to be exposed.

---

## Next Steps
1. Finalise and deploy Lambda function with SES/SNS integration.
2. Configure CloudWatch custom metrics and dashboard.
3. Connect API Gateway endpoint to frontend form.
4. Test and verify that no PII is stored while ensuring thank-you messages are delivered.

---

**End of Document**
