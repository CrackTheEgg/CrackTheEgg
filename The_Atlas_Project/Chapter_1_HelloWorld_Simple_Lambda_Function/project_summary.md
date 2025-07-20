# Atlas Project 1 — AWS Architecture Summary

This project demonstrates core AWS solution architecture skills by deploying a secure, serverless, and observable Hello World API. Designed for portfolio visibility, it includes IAM, Lambda, API Gateway, CloudWatch, and WAF configuration with security-first principles.

---

## 📅 Project Objectives

- 🔗 **Live Demo**: [Hello World API Endpoint](https://j48isil1b9.execute-api.eu-north-1.amazonaws.com/default/HelloWorld)
- Deploy a simple Hello World application using **AWS Lambda + API Gateway**
- Secure the API using **AWS WAF with managed and custom rules**
- Implement logging, monitoring, and IAM best practices
- Prepare clean, production-grade documentation and screenshots for GitHub/CV

---

## 🧭 Project Architecture

![Project Architecture Diagram](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/The_Atlas_Project/Chapter_1_HelloWorld_Simple_Lambda_Function/architectural_diagrams/Chapter_1_Lambda_Hello_World.drawio_rev_1.png)
*Architecture showing API Gateway → Lambda → CloudWatch, with WAF layer for security.*

---


## 🔒 IAM Configuration
- Created IAM **User Group**: `atlas-admins`
- Attached policy: `AdministratorAccess`
- Created named user `Atlas_Project_1` for scoped access
- Attached inline policy to allow only specific Lambda invocation
- Enabled **MFA** and access keys for CLI/API use
  
#### *IAM group and user created with scoped access permissions.*
![IAM Role Configuration](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/The_Atlas_Project/Chapter_1_HelloWorld_Simple_Lambda_Function/P1_Assets/IAM-1.png)

&nbsp;  

#### *IAM user Atlas_Project_1 with inline Lambda invoke permissions.*
![IAM Policy Assignment](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/The_Atlas_Project/Chapter_1_HelloWorld_Simple_Lambda_Function/P1_Assets/IAM-2.png)


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
&nbsp;
  
- Triggered via **REST API Gateway**
- Deployed to `default` stage with `ANY` method support
- Execution role includes `AWSLambdaBasicExecutionRole` for logging

#### *Lambda function source code for Hello World.*
![Lambda Function Configuration](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/The_Atlas_Project/Chapter_1_HelloWorld_Simple_Lambda_Function/P1_Assets/Lambda-1.png)

&nbsp;  

#### *Test result confirming successful function execution.*
![Lambda Code Test](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/The_Atlas_Project/Chapter_1_HelloWorld_Simple_Lambda_Function/P1_Assets/Lambda-2%20-%20Code%20Test.png)


---

## 📡 API Gateway Integration
- Configured **REST API** with regional endpoint
- Method: `ANY`
- Resource path: `/HelloWorld`
- Successfully tested using API Gateway console + Postman
- Verified response and latency under 2ms execution time

#### *API Gateway configured to invoke the Lambda function.*  
![API Gateway Setup](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/The_Atlas_Project/Chapter_1_HelloWorld_Simple_Lambda_Function/P1_Assets/API-1.png)

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

#### *WAF rule created to protect API Gateway endpoint.*
![WAF Rule Setup](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/The_Atlas_Project/Chapter_1_HelloWorld_Simple_Lambda_Function/P1_Assets/WAF-1.png)

&nbsp;  

#### *WAF associated with CloudFront distribution or API Gateway stage.*
![WAF Association](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/The_Atlas_Project/Chapter_1_HelloWorld_Simple_Lambda_Function/P1_Assets/WAF-2.png)

---

## 📊 Monitoring & Logs
- **CloudWatch Logs** show execution metrics and logs per invocation
- **CloudWatch Metrics**:
  - Invocations, Errors, Duration, Throttles
- Logs include request ID, memory usage, billing duration, and custom logging

#### *CloudWatch logs confirm the Lambda function was triggered successfully.*
![CloudWatch Logs - 1](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/The_Atlas_Project/Chapter_1_HelloWorld_Simple_Lambda_Function/P1_Assets/CloudWatch%20logs%20-%201.png)

&nbsp;

#### *CloudWatch shows detailed log stream for execution lifecycle.*
![CloudWatch Logs - 2](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/The_Atlas_Project/Chapter_1_HelloWorld_Simple_Lambda_Function/P1_Assets/CloudWatch%20Logs-2.png)
&nbsp;

#### *Log metrics provide invocation and performance insights.*
![CloudWatch Logs - 3](https://raw.githubusercontent.com/CrackTheEgg/CrackTheEgg/main/The_Atlas_Project/Chapter_1_HelloWorld_Simple_Lambda_Function/P1_Assets/CloudWatch%20Logs-3.png)

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
