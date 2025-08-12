# Chapter 2 – CV Website (Summary)

## Project Overview
The goal of Chapter 2 was to deploy a static CV website using AWS S3, CloudFront, Route 53, and ACM for HTTPS.  
This chapter demonstrates how to host, secure, and deliver a static site on AWS with a professional domain name.

## Architecture
- **Amazon S3** – Stores the static HTML, CSS, JS, and image assets.
- **Amazon CloudFront** – Distributes the site globally with low latency and HTTPS.
- **AWS Certificate Manager (ACM)** – Provides the SSL/TLS certificate for secure HTTPS connections.
- **Amazon Route 53** – Manages the DNS for `christianhegarty.com`.

## HTML and CSS Implementation
- **HTML** – The CV page was built using a semantic HTML structure for accessibility and SEO.  
  Sections include a fixed hero header, a scrollable CV timeline, and clickable certification badges linking to official credentials.
- **CSS** – A **global stylesheet** was implemented (`global.css`) to standardise typography, layout, and styling across all site pages.  
  - Uses CSS variables for font sizes, line heights, and colours.  
  - Implements reusable class structures (e.g., `.main-container`, `.scroll-box`, `.content-block`).  
  - Ensures responsiveness with fluid widths and media queries.
- **Design Approach** – The design matches the style of the portfolio landing page for brand consistency.

## Key AWS Concepts Demonstrated
- **Static Website Hosting** – Using S3 to serve a complete portfolio site.
- **Custom Domain Integration** – Configured Route 53 to point to the CloudFront distribution.
- **Edge Caching & HTTPS** – Used CloudFront for performance and security.
- **Security Best Practice** – S3 bucket is private, with access granted only via CloudFront Origin Access Control.

## Why This Matters
This project demonstrates a production-grade, secure, and scalable static website deployment.  
It also provides the foundation for **Chapter 3**, which will build on this by introducing multi-origin CloudFront routing for separate project pages.