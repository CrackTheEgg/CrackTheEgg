# Project Brief – Chapter 01: Lambda Hello World

**Project Name:** Hello World Micro-Service  
**Requested By:** Internal Product Innovation Team  
**Submitted:** July 11, 2025  
**Prepared For:** Solutions Architecture Review  

---

## 🧩 Background
Our internal development team is exploring AWS cloud services and wants to experiment with building microservices using **serverless architecture**. The goal is to reduce operational overhead and evaluate how AWS Lambda fits into our long-term DevOps strategy.

---

## 🎯 Objective
We need a simple proof-of-concept (PoC) Lambda function that:
- Runs without provisioning or managing servers
- Responds to an HTTP request or event trigger
- Returns a simple "Hello World" message

This PoC will be used to demonstrate:
- Serverless function setup
- IAM permissions management
- Event triggering (manual or via API Gateway)
- Monitoring via AWS Console

---

## 📦 Deliverables
- Lambda function returning "Hello from Lambda!"
- IAM role with least-privilege access
- Test event configuration OR HTTP endpoint
- README documentation of the deployment steps
- Optional: AWS architecture diagram

---

## 📅 Timeline
We need this PoC deployed and working by end of the week for a team demo. No production-grade security or scaling is needed at this stage.

---

## 💸 Budget
Use the AWS Free Tier where possible. Keep costs negligible.

---

## 🧠 Success Criteria
- Can invoke the function and see the expected output
- Clear documentation of setup and deployment
- No persistent infrastructure (must be serverless)
