# Solution Design Document

**Prepared and Presented by:**
- Cerio, Jennifer
- De Guzman, Catherine
- Valerio, Redentor
-Denolan, Honey Grace 

**Course:** BSIT  
**Term:** 3 SY 2024-2025

---

## Intellectual Property Notice

This template is an exclusive property of Mapua-Malayan Digital College and is protected under Republic Act No. 8293, also known as the Intellectual Property Code of the Philippines (IP Code). It is provided solely for educational purposes within this course. Students may use this template to complete their tasks but may not modify, distribute, sell, upload, or claim ownership of the template itself. Such actions constitute copyright infringement under Sections 172, 177, and 216 of the IP Code and may result in legal consequences. Unauthorized use beyond this course may result in legal or academic consequences.

Additionally, students must comply with the Mapua-Malayan Digital College Student Handbook, particularly with the following provisions:

**Offenses Related to MMDC IT:**
- Section 6.2 – Unauthorized copying of files
- Section 6.8 – Extraction of protected, copyrighted, and/or confidential information by electronic means using MMDC IT infrastructure

**Offenses Related to MMDC Admin, IT, and Operations:**
- Section 4.5 – Unauthorized collection or extraction of money, checks, or other instruments of monetary equivalent in connection with matters pertaining to MMDC

Violations of these policies may result in disciplinary actions ranging from suspension to dismissal, in accordance with the Student Handbook.

For permissions or inquiries, please contact MMDC-ISD at [isd@mmdc.mcl.edu.ph](mailto:isd@mmdc.mcl.edu.ph).

---

## Table of Contents

| Section | Topic |
|---------|-------|
| I | Introduction |
| II | Control Selection and Justification |
| III | Control Mapping Table |
| IV | Compliance Considerations |
| V | Final Design Summary |

---

## I. Introduction

### Project/System Overview

**Connectly** is a backend-only RESTful API developed using Django, designed to deliver essential social media functionalities such as posting, commenting, liking, and personalized feed retrieval. It is built for integration with any frontend or mobile application, offering flexibility and scalability across platforms. 

Key features include:
- Token-based authentication (standard login and Google OAuth)
- Role-based access control (RBAC)
- Redis caching for performance optimization
- Centralized logging for monitoring and diagnostics

As an API-first system with public-facing endpoints, Connectly is inherently exposed to common web-based threats. Since it processes user-generated content and sensitive information such as login credentials and session tokens, robust security controls are essential to ensure system reliability, data protection, and user privacy.

### Key Risks and Vulnerabilities

The following high-priority risks have been identified as critical areas requiring immediate mitigation:

1. **Brute-force login attacks** – The public login endpoint currently lacks any rate limiting or CAPTCHA mechanism, allowing automated bots to attempt credential stuffing attacks.

2. **SQL injection** – User input fields, particularly in post and comment endpoints, are vulnerable to injection if not properly sanitized, potentially compromising database integrity.

3. **JWT token exposure in logs** – Without proper log filtering, full session tokens may be inadvertently written to logs, enabling attackers to hijack sessions.

4. **Broken access control** – Inadequate enforcement of user roles could lead to unauthorized users viewing or modifying private content, violating user confidentiality.

5. **SECRET_KEY exposure** – Project secrets, including Django's SECRET_KEY, may be accidentally exposed in version-controlled repositories, which would compromise the entire authentication system.

6. **Cache poisoning** – Feed content could be manipulated via malformed or unvalidated cache keys, affecting data integrity and user experience.

7. **Unencrypted sensitive data and lack of recovery** – Without encryption and proper backup configuration, sensitive data stored in the database is vulnerable to unauthorized access, data loss, or corruption. This threatens both confidentiality and availability, especially in the event of a breach, hardware failure, or disaster.

These risks target multiple components of the CIA Triad — with major impacts on **Confidentiality (C)**, **Integrity (I)**, and **Availability (A)** — and require structured, defense-in-depth controls to reduce exposure and potential damage.

### Security Objectives

To address the above risks, the project aims to:

- **Protect sensitive data**, including login credentials, tokens, and private content, from unauthorized access and exposure.
- **Prevent unauthorized system access** through secure authentication, input validation, and strict RBAC enforcement.
- **Ensure data integrity** by mitigating injection threats, securing cache operations, and validating all user input.
- **Maintain availability and system stability** by minimizing automated attack vectors and ensuring reliable error handling and logging.
- **Align with legal and industry standards**, including the Data Privacy Act of 2012 (RA 10173), ISO/IEC 27001, and OWASP Top 10, to ensure ethical, regulatory-compliant system development.

Together, these objectives will guide the design and implementation of practical, scalable, and effective security solutions that safeguard the Connectly API throughout its development lifecycle.

---

## II. Control Selection and Justification (with CBA Insights)

To address the most critical risks identified in the Threat and Vulnerability Assessment, several security controls were selected based on their relevance, alignment with industry standards, and cost-efficiency. The selection follows the principles of **Defense-in-Depth**, **Zero Trust Architecture**, **Secure Data Flow Design**, and **Network Segmentation**.

While all controls contribute to overall system resilience, a focused Cost-Benefit Analysis (CBA) was conducted for four priority controls to ensure practical investment decisions. These controls were selected due to their direct impact on high-risk areas and their potential to significantly reduce the cost of security incidents.

### 1. JWT Token Redaction in Logs

The first control targets the exposure of JWT tokens in logs. As a **preventive strategy**, this control involves modifying the system's logging configuration to filter out or redact sensitive fields, including session tokens, passwords, and authentication headers. It minimizes the risk of session hijacking by preventing leaked logs from being exploited. This aligns with NIST SP 800-92 and ISO/IEC 27001 Annex A.12.4.1, both of which emphasize the importance of protecting sensitive data in event logs.

**Cost-Benefit Analysis Results:**
- **Estimated annual cost:** ₱60,000 (primarily for DevOps integration and log sanitization tooling)
- **Expected prevention:** ₱1,000,000 in breach-related losses from token misuse
- **Outcome:** **Highly Justified** — delivering strong security at a reasonable cost

### 2. Role-Based Access Control (RBAC)

The second control enforces Role-Based Access Control (RBAC). This control is both **preventive and detective**, using Django's permission framework and middleware to ensure that each user can only access resources allowed by their role (e.g., admin, user, guest). It prevents unauthorized access and detects violations through role-level audit trails. RBAC aligns with OWASP A01:2021 Broken Access Control, ISO/IEC 27001 Annex A.9.1.2, and CIS Control 6.1, and is fundamental in maintaining access boundaries in multi-user systems.

**Cost-Benefit Analysis Results:**
- **Estimated annual cost:** ₱120,000
- **Expected prevention:** ₱850,000 in unauthorized data exposure or privilege escalation incidents
- **Outcome:** **Justified** — offering substantial protection in multi-user environments

### 3. Database Encryption and Backup

This control secures at-rest data and supports recovery in the event of data loss, corruption, or unauthorized access. As a **preventive measure**, it involves configuring PostgreSQL with pgcrypto for encryption and setting up automated encrypted backups using cloud platforms such as AWS RDS or Oracle Cloud. This ensures that even if data is compromised, it remains unreadable and recoverable, supporting business continuity and data resilience. The control is aligned with ISO/IEC 27001 standards on data protection, availability, and backup management.

**Cost-Benefit Analysis Results:**
- **Estimated annual cost:** ₱200,000
- **Expected prevention:** ₱900,000 in breach response and data recovery
- **Outcome:** **Partially Justified** — higher cost but essential for long-term resilience and regulatory compliance

### 4. Environment-Based Secret Management (.env)

This control addresses secret management via environment variables, tackling the risk of SECRET_KEY and credential exposure in source code repositories. As a **preventive control**, all sensitive credentials are stored in .env files or managed using secure tools such as HashiCorp Vault or AWS Secrets Manager. These credentials are excluded from version control using .gitignore, preventing unintentional leaks. This practice aligns with the OWASP Application Security Verification Standard (ASVS 4.0) and supports secure development as outlined in ISO/IEC 27001 Annex A.9.2.4 and DevSecOps principles.

**Cost-Benefit Analysis Results:**
- **Estimated annual cost:** ₱15,000
- **Expected prevention:** ₱700,000 in exploits caused by exposed credentials
- **Outcome:** **Highly Justified** — high security return at minimal cost

### 5. Input Validation and ORM-Based Query Handling

This control involves input validation and ORM-based query handling, which mitigates the risk of SQL injection in post and comment fields. As a **preventive control**, Django forms and serializers are used to validate user input, while the Django ORM ensures all database interactions use parameterized queries. This dual-layered approach blocks malicious inputs before they reach sensitive components. It aligns with the OWASP Top 10 (A03:2021 Injection), ISO/IEC 27001 Annex A.14.2.5, and CIS Control 16.7, making it a strong defense against one of the most common and dangerous web application vulnerabilities.

> **Note:** Although not included in the formal CBA, this control is still recommended for implementation due to its critical role in protecting data integrity and application logic. The cost is embedded in core development work and is justified by the risk reduction it provides.

### 6. Rate Limiting for Login API

To prevent brute-force attacks, this control limits the number of login attempts from a single IP or user within a specified timeframe using Django middleware (e.g., django-ratelimit) or external protection services such as Cloudflare. It may include lockouts or CAPTCHA challenges after repeated failures and is aligned with OWASP's Authentication Cheat Sheet, NIST SP 800-63B, and CIS Control 4.6, all of which emphasize mitigating automated login abuse. This control is considered both **preventive and detective**: preventive because it blocks excessive login attempts before they succeed, and detective because it enables logging and alerting of suspicious login behavior for further investigation.

> **Note:** Although this control was not included in the Cost-Benefit Analysis, it is regarded as an essential early-stage security measure. Its implementation cost is expected to be moderate, and the security value is significant, particularly in protecting user accounts and reducing the risk of automated system compromise.

### 7. Cache Key Validation and Hashing

Lastly, to prevent cache poisoning, this control implements cache key validation and sanitization. This is a **preventive measure** that validates all user input used in cache operations and applies secure hashing algorithms such as SHA-256 before generating Redis keys. This ensures consistent and safe key formatting, preventing attackers from manipulating cache entries. It aligns with OWASP caching best practices and contributes to data integrity under CIS Control 13.

> **Note:** This control was not prioritized in the CBA but is considered low-cost and effective, especially in securing content and user feeds from manipulation.

Collectively, these controls provide a robust foundation for securing the Connectly API backend, each selected for its relevance to the identified risks and its ability to reinforce confidentiality, integrity, and availability across the system.

### Cost Benefit Analysis (CBA) Table

This Cost-Benefit Analysis evaluates the financial viability and security impact of the proposed controls for the Connectly API system. Each control is assessed based on its annual estimated implementation cost, associated tools or technologies, the specific risk it mitigates, and the projected financial savings from avoiding breaches or data loss.

The outcome for each control is categorized as:
- **Highly Justified** controls offer substantial protection at relatively low cost, directly addressing high-impact vulnerabilities
- **Justified** controls are crucial for system integrity and access management in multi-user environments, with clear security returns
- **Partially Justified** controls involve higher upfront or operational costs but are still essential for long-term resilience and compliance

| Control | Estimated Cost (Annual) | Tools / Implementation | Risk Reduction | Potential Savings | CBA Outcome |
|---------|------------------------|------------------------|----------------|-------------------|-------------|
| JWT Token Reduction | ₱60,000 | Use of centralized logging tools like ELK Stack (Elasticsearch, Logstash, Kibana) with log sanitizers and token filters | Prevents session hijacking from token leakage | Saves ₱1,000,000 in breach cost | **Highly Justified** — critical protection vs. credential abuse |
| RBAC Enforcement | ₱120,000 | Role control using Django middleware, integrated with LDAP/SSO (if scaled); Dev-time + auditing overhead | Limits access to authorized users only | Prevents ₱850,000 in Data Exposure Cost | **Justified** — essential for secure multi-user operations |
| DB Encryption & Backup | ₱200,000 | PostgreSQL with pgcrypto, automated nightly backups via AWS RDS/Oracle Cloud, encrypted volumes | Secures at-rest data and supports recovery | Saves ₱900,000 in recovery/loss | **Partially Justified** — high upfront cost but essential safety |
| Environment-Based Secret Management (.env) | ₱15,000 | Secrets stored in environment variables or HashiCorp Vault / AWS Secrets Manager | Prevents credential leaks from source code | Avoids ₱700,000 in exploits | **Highly Justified** — minimal cost, very high risk mitigation |

---

## III. Control Mapping Table

The Control Mapping Table summarizes how each selected security control addresses specific risks identified in the system. It links each risk or vulnerability to the corresponding control type (e.g., Preventive, Detective), provides a brief description of the control, and explains the justification behind its selection. This table ensures that all critical threats are mapped to appropriate security measures, helping visualize the coverage and alignment of controls with overall security objectives.

| Risk / Vulnerability | Control Type | Control Description | System Layer | Data Flow Protection | Justification |
|---------------------|--------------|-------------------|--------------|---------------------|---------------|
| Brute-force login via public API | Preventive / Detective | Implement rate limiting on login attempts using Django middleware or API gateway | Perimeter (API Gateway) | ✔ | Reduces automated login abuse; aligns with OWASP and NIST SP 800-63B guidelines |
| SQL injection in post/comment input fields | Preventive | Use Django ORM and apply input validation with serializers and forms | Application | ✔ | Avoids raw queries; protects against OWASP Top 10 A03:2021 Injection attacks |
| JWT tokens exposed in logs | Preventive | Sanitize logs to redact sensitive fields like tokens and passwords | Application/Infrastructure | ✔ | Prevents session hijacking; aligns with NIST SP 800-92 and ISO 27001 logging practices |
| Broken access control exposing private content | Preventive / Detective | Enforce RBAC using Django's permission system and middleware-level role checks | Application | ✔ | Prevents privilege escalation and unauthorized access; supports OWASP ACVS |
| SECRET_KEY exposure through source control | Preventive | Store secrets in environment variables or .env files excluded from Git | Infrastructure | ✔ | Follows 12-Factor App best practices; avoids credential leakage in repositories |
| Cache poisoning via unvalidated user keys | Preventive | Sanitize and hash inputs before using them in Redis cache key generation | Application/Data | ✔ | Prevents feed manipulation; aligns with OWASP caching best practices |
| Unencrypted sensitive data and lack of recovery | Preventive | Encrypt at-rest data using PostgreSQL pgcrypto and configure automated backups with AWS RDS or Oracle Cloud | Data | ✔ | Protects confidential data and enables recovery; supports ISO/IEC 27001 controls on backup and storage |

---

## IV. Compliance Considerations

The Compliance Considerations Table outlines the security controls that are specifically implemented to meet legal, regulatory, or industry standards. It links each control to a relevant framework (such as the Data Privacy Act of 2012, ISO/IEC 27001, OWASP, or NIST), and explains how the control supports compliance. This ensures that the system is not only technically secure but also aligned with external requirements for data protection, privacy, and responsible system management.

| Control Description | Applicable Framework/Standard | Compliance Justification |
|--------------------|-------------------------------|--------------------------|
| Redaction of JWT tokens and sensitive data from system logs | Data Privacy Act (RA 10173)<br>ISO/IEC 27001 | Prevents exposure of personal and session data in logs, ensuring protection of user information under DPA Section 11. |
| RBAC (Role-Based Access Control) implementation | ISO/IEC 27001 Annex A.9.1.2<br>DPA Section 20 | Enforces the principle of least privilege, limiting access to data based on roles, as required by both frameworks. |
| Secure secret management using environment variables | OWASP ASVS<br>ISO/IEC 27001 Annex A.9.2.4 | Ensures system credentials (e.g., SECRET_KEY) are not exposed in repositories or public code, preventing breaches. |
| Input validation and safe query handling (SQL injection prevention) | OWASP Top 10 (A03:2021)<br>ISO/IEC 27001 | Defends against one of the most common web attacks, preserving data integrity and aligning with secure coding practices. |
| Rate limiting for login endpoints | NIST SP 800-63B<br>CIS Control 4.6 | Limits automated credential attacks and supports user account protection, fulfilling guidance on authentication security. |
| Database encryption and backup configuration | ISO/IEC 27001 Annex A.10.1 & A.12.3.1 | Protects sensitive data at rest and supports secure backup and recovery procedures, aligning with controls on cryptographic protection and information backup. |

---

## Security Architecture Diagram

Our system uses a multi-zone layered architecture aligned with Defense-in-Depth. Controls such as rate limiting (perimeter), RBAC and input validation (application), and encryption (data layer) are mapped across the architecture to protect data flow from client to storage. Zones are separated to enforce network segmentation and zero trust boundaries.

### Architecture Zones:

#### External Zone:
**Web/Mobile Clients + Google OAuth**
- Mitigates brute force and SQL injection via OAuth, input validation, and rate limiting.

#### Perimeter Zone:
**API Gateway / Load Balancer**
- Handles SSL termination, request filtering, and basic DDoS protection.

#### Application Zone:
**Django REST API**
- Secures authentication, authorization, and input validation
- Enforces business logic and logs activities

#### Data Zone:
**PostgreSQL, Redis, Log Storage**
- Encrypted data storage, internal-only access, and secure logging

#### Infrastructure Zone:
**Secret Management**
- Manages API keys and credentials with strict access control and regular rotation

To prevent data interception, manipulation, or leakage, the architecture integrates controls across all flow points. TLS ensures encryption in transit, input validation prevents malicious data during processing, and database encryption secures data at rest. By embedding these protections within their respective zones, the system ensures that data maintains its confidentiality, integrity, and availability end-to-end.

---

## V. Final Design Summary

This Solution Design Document presents a secure architectural blueprint for the Connectly API backend, addressing the most critical risks identified through the Risk Register and Threat & Vulnerability Assessment (TVA). The design mitigates key threats such as brute-force login attacks, SQL injection, JWT token exposure, broken access control, and credential leaks through a layered set of preventive and detective controls.

Security investments were prioritized based on both risk severity and cost-effectiveness, as evaluated through a focused Cost-Benefit Analysis (CBA). Four key controls—JWT Token Redaction, RBAC Enforcement, Database Encryption and Backup, and Environment-Based Secret Management—were analyzed in detail. JWT redaction and secret management were deemed **Highly Justified**, offering significant risk reduction at minimal cost. RBAC was **Justified** for its role in securing multi-user environments, while encryption and backup—though **Partially Justified**—remained essential for long-term data resilience and regulatory compliance.

The design follows core security principles such as **Defense-in-Depth**, **Zero Trust Architecture**, and **Secure Data Flow Design**. Each system layer—from API gateway to infrastructure—is equipped with targeted controls that protect data in transit, during processing, and at rest. Compliance considerations were integrated throughout the design, aligning with frameworks like ISO/IEC 27001, OWASP Top 10, NIST SP 800, and the Data Privacy Act of 2012 (RA 10173).

By strategically implementing controls with high return on investment and focusing on the most exploitable vulnerabilities (e.g., brute-force entry, token leakage, SQL injection), the design achieves a well-balanced mix of security effectiveness, operational feasibility, and cost-efficiency. This ensures the Connectly API is not only secure and compliant but also scalable and maintainable in a real-world deployment context.
