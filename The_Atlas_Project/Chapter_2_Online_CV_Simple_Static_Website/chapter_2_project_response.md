# 📄 Project Response – Chapter 02: Online CV Website

---

## BACKGROUND

In response to the client’s request for a professional, cost-effective online CV, this solution outlines a static website hosted entirely within AWS infrastructure. The project builds upon Chapter 01 by continuing to follow a secure, serverless-first design pattern that leverages AWS Free Tier services.

---

## OBJECTIVE

To build and deploy a responsive, personal CV site that:

- Presents a modern and professional layout
- Includes key information: Work History, Education, Skills, AWS Portfolio
- Links directly to Project Atlas and GitHub repositories
- Operates entirely within the AWS Free Tier
- Demonstrates scalable serverless architecture principles

---

## SOLUTION ARCHITECTURE

### Components

- **HTML/CSS Static Website** – Core CV and portfolio site
- **Amazon S3** – Static hosting with public access
- **Amazon CloudFront** – CDN for performance and HTTPS support
- **IAM** – Scoped user permissions for secure updates
- **(Optional)** **Amazon Route 53** – Custom domain mapping

### Architecture Flow

```
User Request → CloudFront CDN → S3 Static Website Bucket
```

---

## SECURITY & IAM

- IAM User `Atlas_Project_2` created and added to `atlas-admins` group
- Permissions scoped to S3 and CloudFront operations only
- MFA and access keys configured for secure CLI/API deployment

---

## DEPLOYMENT STRATEGY

**Method:** Manual deployment via AWS Console, with version control via GitHub

**Steps:**

1. Create and test static HTML/CSS content locally
2. Configure S3 bucket for public static hosting
3. Upload site files via S3 console or CLI
4. Set up CloudFront distribution with default root object
5. (Optional) Map custom domain using Route 53 and AWS Certificate Manager for HTTPS

---

## DOCUMENTATION STRATEGY

- Annotated HLD to illustrate static hosting architecture
- Optional LLDs if site features become more interactive in future phases
- Screenshots for IAM, S3, and CloudFront setup
- Markdown-based README files and commentary to accompany GitHub repo

---

## SUCCESS CRITERIA

- Public static website renders successfully
- Responsive layout across desktop and mobile
- GitHub and Project Atlas links embedded and functional
- Hosted fully within AWS Free Tier boundaries
- Architecture and process clearly documented

---

## FUTURE CONSIDERATIONS

- Convert to React or static site generator (e.g. Hugo)
- Automate S3 deployment using GitHub Actions or Amplify
- Introduce analytics via CloudWatch or third-party JS snippets
- Add a blog or update feed using a headless CMS

---

**End of Project Response – Chapter 02**

