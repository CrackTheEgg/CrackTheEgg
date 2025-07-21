# 📄 Project Response – Chapter 02: Static Online CV

---

## BACKGROUND

This document outlines the proposed solution for a modern, static online CV site. The goal is to showcase an individual's professional background, education, and a portfolio of AWS projects, continuing the "golden thread" established in Project 1.

---

## OBJECTIVE

To design and deploy a lightweight, responsive, and cost-effective personal CV site hosted on AWS, with emphasis on:

- Clear, accessible design with professional tone
- Structured content including Work History, Education, Skills, and AWS Projects
- Integrated links to GitHub and Project Atlas
- Fully serverless and Free Tier-eligible architecture

---

## SOLUTION ARCHITECTURE

### Components:

- **HTML/CSS Static Website** – Personal branding site
- **Amazon S3** – Static hosting bucket
- **Amazon Route 53** *(optional)* – Custom domain DNS
- **Amazon CloudFront** – CDN + HTTPS
- **IAM** – Scoped user for CV deployment

### Architecture Flow:

```
User Request → CloudFront CDN → S3 Static Site Bucket
```

---

## SECURITY & IAM

- IAM user `Atlas_Project_2` added to `atlas-admins` group
- Scoped IAM policy for deploying to S3 and managing CloudFront
- SSL enabled via AWS Certificate Manager (if custom domain used)

---

## DEPLOYMENT STRATEGY

**Method:**

- Manual deployment using AWS Console or CLI
- Source files managed and versioned in GitHub

**Steps:**

1. Design page layout and static content
2. Configure S3 bucket for static website hosting
3. (Optional) Point custom domain using Route 53
4. Deploy content from GitHub repo via S3 console or CLI
5. Configure CloudFront distribution and attach SSL

---

## DOCUMENTATION STRATEGY

Each major phase is supported with:

- Annotated architectural diagrams (HLD and LLD)
- Screenshots for key AWS steps (IAM, S3, CloudFront, etc.)
- Commentary for reasoning, choices, and learnings

> While daily workflow planning helped guide execution, this document reflects the final state of the solution and is structured for professional clarity.

---

## SUCCESS CRITERIA

- Static website renders fully and securely
- Responsive layout and clean design
- Public link to GitHub project(s) embedded
- No monthly cost under Free Tier
- HLD + LLD accurately reflect the implementation

---

## FUTURE CONSIDERATIONS

- Convert HTML to React with CI/CD pipeline
- Add analytics using CloudWatch or 3rd party tools
- Use Amplify or S3-triggered deploy automation
- Integrate blog or project CMS using Headless CMS

---

**End of Project Response – Chapter 02**

