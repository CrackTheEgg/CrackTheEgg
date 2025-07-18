# Atlas Project 1 — AWS Architecture Summary

This project demonstrates core AWS solution architecture skills by deploying a secure, serverless, and observable Hello World API. Designed for portfolio visibility, it includes IAM, Lambda, API Gateway, CloudWatch, and WAF configuration with security-first principles.

---

## 📅 Project Objectives
- Deploy a simple Hello World application using **AWS Lambda + API Gateway**
- Secure the API using **AWS WAF with managed and custom rules**
- Implement logging, monitoring, and IAM best practices
- Prepare clean, production-grade documentation and screenshots for GitHub/CV

---


## 🔒 IAM Configuration
- Created IAM **User Group**: `atlas-admins`
- Attached policy: `AdministratorAccess`
- Created named user `Atlas_Project_1` for scoped access
- Attached inline policy to allow only specific Lambda invocation
- Enabled **MFA** and access keys for CLI/API use
  
#### *IAM group and user created with scoped access permissions.*
![IAM Group Setup](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/Chapter_01_Lambda_Hello_World/P1_Assets/IAM-1.png)

&nbsp;  

#### *IAM user Atlas_Project_1 with inline Lambda invoke permissions.*
![IAM User Permissions](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/Chapter_01_Lambda_Hello_World/P1_Assets/IAM-2.png)


---

## ✨ Lambda Hello World
- Created **Python Lambda** named `HelloWorld`
- Code returns:
  ```python
  return {
    'statusCode': 200,
    'body': json.dumps('Hello from the Atlas Project!')
  }
  ```
- Triggered via **REST API Gateway**
- Deployed to `default` stage with `ANY` method support
- Execution role includes `AWSLambdaBasicExecutionRole` for logging

![Lambda Code Setup](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/Chapter_01_Lambda_Hello_World/P1_Assets/Lambda-1.png)
#### *Lambda function source code for Hello World.*

&nbsp;

![Lambda Test Result](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/Chapter_01_Lambda_Hello_World/P1_Assets/Lambda-2%20-%20Code%20Test.png)
#### *Test result confirming successful function execution.*

---

## 📡 API Gateway Integration
- Configured **REST API** with regional endpoint
- Method: `ANY`
- Resource path: `/HelloWorld`
- Successfully tested using API Gateway console + Postman
- Verified response and latency under 2ms execution time

![API Gateway Trigger](../images/Screenshot%202025-07-18%20at%208.10.47%E2%80%AFam.png)
*API Gateway configured with Lambda trigger and default stage.*

---

## Ὦ1️ WAF Web ACL: `Atlas_Project_1`
Applied a layered security model with WAF v2:

### WAF Rule Titles
- **IP Reputation Filter** → Blocks known malicious IPs
- **Bad Input Detection** → Rejects malformed/suspicious payloads
- **Rate Limiting** → Limits to 10 req per 5 minutes/IP
- **Core OWASP Protection** → Covers SQLi, XSS, etc.
- **Default Allow** → Allows if no rule matches
- **Sample Requests Enabled** → Diagnostic sampling active

![WAF Rule Set](../images/Screenshot%202025-07-18%20at%208.20.55%E2%80%AFam.png)
*WAF rules applied to the Hello World API endpoint.*

![WAF Logging Enabled](../images/Screenshot%202025-07-18%20at%208.21.20%E2%80%AFam.png)
*Logging and sample requests enabled in WAF.*

---

## 📊 Monitoring & Logs
- **CloudWatch Logs** show execution metrics and logs per invocation
- **CloudWatch Metrics**:
  - Invocations, Errors, Duration, Throttles
- Logs include request ID, memory usage, billing duration, and custom logging

![CloudWatch Metrics](../images/Screenshot%202025-07-18%20at%207.34.07%E2%80%AFam.png)
*CloudWatch metrics for Lambda performance and reliability.*

![CloudWatch Logs](../images/Screenshot%202025-07-18%20at%207.34.47%E2%80%AFam.png)
*Recent invocations and execution performance logs.*

---

## 📄 Deliverables
- Documented screenshots of:
  - IAM Group/User setup
  - Lambda function and code
  - API Gateway integration
  - Test execution
  - CloudWatch metrics/logs
  - WAF configuration and rule order
- Commentary for each screenshot included in GitHub repo

---

## 🏆 Skills Demonstrated
- AWS Lambda (Python runtime)
- Amazon API Gateway (REST API)
- AWS WAF v2 (regional scope)
- IAM policies and roles
- CloudWatch monitoring and logs
- Secure, observable, serverless design pattern

---

> This project is the foundation of a repeatable deployment pattern used in future AWS Solutions Architect practices and portfolio builds.
