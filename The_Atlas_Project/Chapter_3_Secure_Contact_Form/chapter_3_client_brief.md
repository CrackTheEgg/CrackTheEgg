# Chapter 3 – Secure Contact Form

## Client Brief

**Project Name:** Chapter 3 – Secure Contact Form  
**Date:** 2025-08-12  

The client requires a secure, web-based contact form to be integrated into their existing static website. The form should allow a user to enter either an **email address** or a **mobile phone number** (or both), choose their preferred reply method, and optionally add a short message.

### Functional Requirements
- Upon submission, the system must:
  1. Send an **immediate thank-you message** to the user’s chosen contact method.
     - If email is selected, send via **Amazon SES**.
     - If SMS is selected, send via **Amazon SNS**.
     - If “either” is selected, send via both channels.
  2. **Count each engagement** and record it in **CloudWatch Custom Metrics** for:
     - Total engagements.
     - Number of replies by type (`email`, `sms`, `either`).
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