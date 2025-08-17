# Chapter 3 – Secure Contact Form

## Client Brief

**Project Name:** Chapter 3 – Secure Contact Form  
**Date:** 2025-08-12  

**Clinet Objective** Enable visitors to send secure messages without storing personal data, ensuring high deliverability and minimal spam.

### Functional Requirements
- Upon submission, the system must:

	1. Secure web-to-email / web-to-SMS pipeline (no persistent storage of PII)
      •	Spam prevention (honeypot, bot detection, throttling)
      •	TLS encryption end-to-end
      •	Cross-Origin Resource Sharing (CORS) restricted to portfolio domain
      •	Logging & monitoring for message failures and API usage
      •	Low-cost, serverless-first approach

  2. **Count each engagement** and record it in **CloudWatch Custom Metrics** for:
     - Total engagements.
     - Number of replies by type (`email`, `sms`, `both`).
- **No personal contact details or message content** are to be stored after processing.

### Security Requirements
- **Input validation** for email addresses and phone numbers (E.164 format).
- **Spam/bot protection** using:
  - Honeypot field.
  - Render-time token with a minimum submission delay.
- **CORS restrictions**: Allow only the production domain (`https://christianhegarty.com`).
- **Least-privilege IAM roles** for all AWS services used.
- **No PII in logs**; only redacted metadata (e.g., `hasEmail: true/false`).

### Reporting Requirements
- Use **CloudWatch Metrics** to track:
  - Total engagements.
  - Engagement counts by reply type.
- Data to be viewable in a **CloudWatch Dashboard** for ongoing reporting.

### Constraints ###

  • Must integrate seamlessly with existing static portfolio site (Chapter 2)
	•	No third-party SaaS for email (AWS native preferred)
	•	Minimal operational overhead

### Out of Scope
- Persistent storage of PII or messages (will be addressed in a future chapter).
- Advanced analytics or DynamoDB integration.

---

## Summary
This project builds on:
- **Chapter 1**: Serverless API using AWS Lambda + API Gateway.
- **Chapter 2**: Secure static website hosting with S3 + CloudFront.

In **Chapter 3**, these components are integrated to deliver a fully functional, secure contact form, demonstrating:
- Frontend–backend integration.
- Serverless communication workflows.
- AWS security best practices.
- Real-time metrics reporting.