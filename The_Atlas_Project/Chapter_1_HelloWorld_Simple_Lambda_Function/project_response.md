# 📘 PROJECT RESPONSE – CHAPTER 01: LAMBDA HELLO WORLD

---

## 🧩 BACKGROUND

This document presents the final solution delivered in response to a fictitious client brief requesting a lightweight, serverless Hello World API. The goal was to demonstrate serverless compute using AWS Lambda, with secure HTTP access, logging, and minimal infrastructure — all within the Free Tier.

---

## 🎯 OBJECTIVE

Deliver a **secure, observable, and publicly accessible** Hello World Lambda API that:

- Executes upon HTTP request  
- Returns a static `"Hello from the Atlas Project!"` response  
- Logs invocation data to **Amazon CloudWatch**  
- Applies **WAF protection** for basic security  
- Complies with AWS Free Tier constraints

---

## 🏗️ SOLUTION ARCHITECTURE

### **AWS Services Used**

- **API Gateway (REST)** – Public HTTP trigger (resource path: `/HelloWorld`)  
- **AWS Lambda** – Python 3.13 function  
- **IAM** – Scoped execution role with logging permissions  
- **Amazon CloudWatch** – Logging and basic metrics  
- **AWS WAF v2** – Rate limiting and managed rule protections  

### **Architecture Flow**

```
User ➝ API Gateway ➝ Lambda ➝ CloudWatch Logs  
                        ↘︎ WAF (Web ACL)
```

A **WAF Web ACL** was associated with the API Gateway stage to provide filtering for malicious inputs and traffic spikes.

---

## 🔐 IAM & SECURITY CONSIDERATIONS

### **Lambda Execution Role Policy**

```json
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
```

### **Security Best Practices Applied**

- Created dedicated **IAM user** (`Atlas_Project_1`) with MFA enabled  
- Scoped IAM execution role to only allow logging  
- Deployed WAF with managed rules (e.g., SQLi, XSS, IP reputation)  
- Rate limit: 10 requests per 5 minutes per IP

---

## 🚀 DEPLOYMENT STRATEGY

### **Deployment Method**

Manual setup via AWS Console (to build foundational familiarity)

### **Steps Completed**

1. Created IAM role and attached logging permissions  
2. Authored **Python Lambda function** inline  
3. Deployed REST **API Gateway** and connected it to Lambda  
4. Created **WAF Web ACL** and attached to API  
5. Verified response and log data  
6. Validated **end-to-end functionality** in browser + Postman  

---

## 📈 OBSERVABILITY & MONITORING

### **CloudWatch Features Used**

- Real-time logging of function output  
- Metrics dashboard for:
  - Invocations  
  - Duration  
  - Errors  
  - Throttles

### **Log Example**

```
START RequestId: abc-123 Version: $LATEST
Hello from the Atlas Project!
END RequestId: abc-123
REPORT RequestId: Duration: 2.34 ms Billed Duration: 3 ms
```

---

## 💡 DESIGN CONSIDERATIONS

- All components remain within **AWS Free Tier**  
- No persistent storage required (stateless)  
- Architecture is simple but production-aligned  
- Ready for CI/CD and IaC in future chapters

---

## ✅ SUCCESS CRITERIA MET

- ✅ Lambda returns correct message  
- ✅ Logs visible in CloudWatch  
- ✅ API Gateway URL publicly accessible:  
  `https://j48isil1b9.execute-api.eu-north-1.amazonaws.com/default/HelloWorld`  
- ✅ WAF active and logging sample requests  
- ✅ IAM policies correctly scoped and validated  

---

## 🔭 FUTURE ENHANCEMENTS

- Automate deployment using **CloudFormation / SAM / Terraform**  
- Add **custom domain + HTTPS (via ACM & Route 53)**  
- Store logs and alerts in **S3 for retention**  
- Integrate **Step Functions** for multi-step workflows  

---

**End of Project Response – Chapter 01**
