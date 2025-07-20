# Atlas Project {{PROJECT_NUMBER}} — {{PROJECT_TITLE}}

This project demonstrates core AWS solution architecture skills by deploying a secure, serverless, and observable {{PROJECT_SUMMARY}}. Designed for portfolio visibility, it includes IAM, Lambda, API Gateway, CloudWatch, and WAF configuration with security-first principles.

---

## 📅 Project Objectives
- {{OBJECTIVE_1}}
- {{OBJECTIVE_2}}
- {{OBJECTIVE_3}}
- {{OBJECTIVE_4}}

---

## 🧭 Project Architecture

![Project Architecture Diagram]({{ARCHITECTURE_IMAGE_URL}})
*Architecture showing {{ARCHITECTURE_DESCRIPTION}}.*

---

## 🔒 IAM Configuration
- Created IAM **User Group**: `{{IAM_GROUP_NAME}}`
- Attached policy: `{{IAM_POLICY}}`
- Created named user `{{IAM_USER_NAME}}` for scoped access
- Attached inline policy to allow only specific Lambda invocation
- Enabled **MFA** and access keys for CLI/API use

#### *IAM group and user created with scoped access permissions.*
![IAM Role Configuration]({{IAM_IMAGE_1}})

&nbsp;

#### *IAM user with inline Lambda invoke permissions.*
![IAM Policy Assignment]({{IAM_IMAGE_2}})

---

## ✨ Lambda Setup
- Created **{{RUNTIME}} Lambda** named `{{LAMBDA_NAME}}`
- Code returns:
  ```{{CODE_LANGUAGE}}
  {{LAMBDA_CODE_SNIPPET}}
  ```
&nbsp;

- Triggered via **{{TRIGGER_SERVICE}}**
- Deployed to `{{STAGE_NAME}}` stage
- Execution role includes `{{IAM_EXECUTION_ROLE}}` for logging

#### *Lambda function source code.*
![Lambda Function Configuration]({{LAMBDA_IMAGE_1}})

&nbsp;

#### *Test result confirming successful function execution.*
![Lambda Code Test]({{LAMBDA_IMAGE_2}})

---

## 📡 API Gateway Integration
- Configured **{{API_TYPE}}** with regional endpoint
- Method: `{{METHOD_TYPE}}`
- Resource path: `{{RESOURCE_PATH}}`
- Successfully tested using console + external clients
- Verified response time and metrics

#### *API Gateway configured to invoke Lambda.*
![API Gateway Setup]({{API_IMAGE}})

---

## 🛡️ WAF Web ACL: `{{WAF_NAME}}`
Applied a layered security model with WAF v2:

### WAF Rules
- **{{RULE_1}}**
- **{{RULE_2}}**
- **{{RULE_3}}**
- **{{RULE_4}}**
- **{{RULE_5}}**

#### *WAF rule created to protect API Gateway.*
![WAF Rule Setup]({{WAF_IMAGE_1}})

&nbsp;

#### *WAF associated with distribution or stage.*
![WAF Association]({{WAF_IMAGE_2}})

---

## 📊 Monitoring & Logs
- **CloudWatch Logs** show execution metrics per invocation
- **CloudWatch Metrics**:
  - Invocations, Errors, Duration, Throttles

#### *CloudWatch logs confirm Lambda execution.*
![CloudWatch Logs - 1]({{LOG_IMAGE_1}})

&nbsp;

#### *CloudWatch shows detailed log stream.*
![CloudWatch Logs - 2]({{LOG_IMAGE_2}})

&nbsp;

#### *Log metrics provide insights.*
![CloudWatch Logs - 3]({{LOG_IMAGE_3}})

---

## 📄 Deliverables
- Documented screenshots of all major steps
- Commentary included inline for clarity
- GitHub-ready formatting

---

## 🏆 Skills Demonstrated
- AWS Lambda ({{RUNTIME}})
- Amazon API Gateway ({{API_TYPE}})
- IAM policies and scoped permissions
- AWS WAF v2
- CloudWatch logs and metrics
- Serverless deployment pattern

---

> This project is part of a repeatable deployment pattern in the Atlas AWS Architecture learning series.
