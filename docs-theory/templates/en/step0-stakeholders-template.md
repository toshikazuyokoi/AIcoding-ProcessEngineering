# Stakeholder List

---
purpose: "A template for stakeholder identification and communication planning for AI-driven software projects"
category: "project-planning"
target_user: "project-manager"
usage_phase: "step0"
related_templates:
  - "step0-goal-statement-template.md"
  - "step0-constraints-template.md"
---

## Metadata
- **Document ID**: STAK-001
- **Related Documents**: 
  - GOAL-001 (Goal Statement)
  - CONST-001 (Constraints List)
  - UC-001 (Use Case List)
  - Quality Gate 1 Checklist
- **Project Phase**: STEP 0 - Goal Definition
- **Created Date**: YYYY-MM-DD
- **Last Updated**: YYYY-MM-DD
- **Author**: [Author Name]
- **Reviewer**: [Reviewer Name]
- **Approver**: [Project Manager Name]
- **Version**: [Version Number]
- **Status**: Draft/Under Review/Approved

## 1. Stakeholder Classification

### 1.1 Stakeholder Map
````mermaid
graph TD
    subgraph "Influence: High"
        A[Executive/Sponsor]
        B[Product Owner]
        C[Key User Representatives]
    end
    
    subgraph "Influence: Medium"
        D[Development Team]
        E[Operations Team]
        F[Quality Assurance Team]
        G[Security Team]
    end
    
    subgraph "Influence: Low"
        H[General Users]
        I[Support Team]
        J[External Vendors]
    end
    
    style A fill:#f99,stroke:#333,stroke-width:3px
    style B fill:#f99,stroke:#333,stroke-width:3px
    style C fill:#f99,stroke:#333,stroke-width:3px
````

### 1.2 Primary Stakeholders (Directly involved in decision-making)
| Role | Name/Organization | Responsibility | Authority Level | Expectations | Concerns | Contact |
|------|-------------------|----------------|-----------------|--------------|----------|---------|
| Project Sponsor | [Name] | • Budget approval<br>• Key decisions<br>• Resource allocation | Final decision authority | • ROI achievement<br>• On-time completion<br>• Quality assurance | • Budget overrun<br>• Schedule delays | [Email/Phone] |
| Product Owner | [Name] | • Requirements definition<br>• Priority decisions<br>• Acceptance criteria | Feature decision authority | • Business value maximization<br>• User satisfaction | • Missing features<br>• Usability issues | [Email/Phone] |
| Technical Lead | [Name] | • Technology selection<br>• Architecture decisions<br>• Technical risk management | Technical decision authority | • Technical excellence<br>• Maintainability | • Technical debt<br>• Skill gaps | [Email/Phone] |
| User Representative | [Name/Dept] | • Requirements input<br>• UAT execution<br>• Feedback | Requirements approval | • Process efficiency<br>• Ease of use | • Learning curve<br>• Business impact | [Email/Phone] |

### 1.3 Secondary Stakeholders (Affect or are affected by the project)
| Role | Name/Organization | Impact | Interest | Involvement Timing | Required Information | Contact |
|------|-------------------|---------|----------|--------------------|---------------------|---------|
| Development Team | [Team Name] | High | • Clear requirements<br>• Proper dev environment<br>• Technical support | All phases | • Specifications<br>• Tech guides<br>• Progress status | [Email/Slack] |
| Operations Team | [Team Name] | High | • Operational ease<br>• Monitoring capability<br>• Incident procedures | Design～Operation | • Operation manual<br>• SLA<br>• Escalation | [Email/Phone] |
| QA Team | [Team Name] | Medium | • Quality standards<br>• Test environment<br>• Defect management | Test～Release | • Test plan<br>• Quality metrics | [Email/Jira] |
| Security Team | [Team Name] | Medium | • Security requirements<br>• Vulnerability mitigation<br>• Audit compliance | Design～Operation | • Security design<br>• Audit logs | [Email] |
| Legal/Compliance | [Dept Name] | Medium | • Regulatory compliance<br>• License management<br>• Contract terms | Requirements～Contract | • Terms of use<br>• Contracts | [Email] |
| Finance/Procurement | [Dept Name] | Low | • Budget management<br>• Cost optimization<br>• Procurement process | Planning～Procurement | • Budget plan<br>• Quotes | [Email] |

### 1.4 External Stakeholders
| Organization/Role | Relationship | Impact | Management Strategy | Contract Type | Contact Point |
|-------------------|--------------|---------|-------------------|---------------|---------------|
| [Vendor Name] | Technology Provider | Medium | Partnership | SLA Agreement | [Contact Name] |
| [Partner Company] | Joint Development | High | Close Collaboration | Joint Development Agreement | [Contact Name] |
| [Regulatory Body] | Oversight | High | Compliance Focus | - | [Contact Dept] |

## 2. Stakeholder Engagement Strategy

### 2.1 Engagement Matrix
| Stakeholder | Current Engagement | Desired Engagement | Gap | Strategy |
|-------------|-------------------|-------------------|-----|----------|
| [Stakeholder 1] | Low/Medium/High | Low/Medium/High | [Gap] | [Strategy] |
| [Stakeholder 2] | Low/Medium/High | Low/Medium/High | [Gap] | [Strategy] |

### 2.2 Power/Interest Matrix
````mermaid
graph LR
    subgraph "High Power・High Interest"
        A[Manage Closely]
        A1[Sponsor]
        A2[Product Owner]
    end
    
    subgraph "High Power・Low Interest"
        B[Keep Satisfied]
        B1[Executives]
        B2[Regulators]
    end
    
    subgraph "Low Power・High Interest"
        C[Keep Informed]
        C1[Dev Team]
        C2[Users]
    end
    
    subgraph "Low Power・Low Interest"
        D[Monitor]
        D1[General Staff]
        D2[External Vendors]
    end
````

## 3. Communication Plan

### 3.1 Regular Communication
| Stakeholder | Meeting/Report | Frequency | Format | Content | Responsible | Deliverable |
|-------------|----------------|-----------|---------|---------|-------------|-------------|
| Project Sponsor | Steering Committee | Monthly | Face-to-face/Web | • Progress status<br>• Issues & solutions<br>• Budget execution | PM | Monthly Report |
| Product Owner | Sprint Review | Bi-weekly | Face-to-face/Demo | • Feature demo<br>• Next sprint plan | Scrum Master | Sprint Report |
| Development Team | Daily Scrum | Daily | Stand-up | • Progress sharing<br>• Issue sharing | Dev Lead | Meeting Notes |
| User Representative | User Meeting | Monthly | Web Meeting | • Requirements confirmation<br>• Feedback | PO | Requirements Update Log |

### 3.2 Event-based Communication
| Event | Target Stakeholders | Method | Timing | Content |
|-------|-------------------|---------|---------|---------|
| Critical Issue | Sponsor, PM | Phone→Email | Within 1 hour | Issue details, impact, solutions |
| Milestone Achievement | All Stakeholders | Email, Portal | Within 1 business day | Achievement details, next steps |
| Specification Change | Affected Parties | Change Control Meeting | Before decision | Change details, impact analysis |
| Release | All Stakeholders | Email, Briefing | 1 week before release | Release content, schedule |

### 3.3 Communication Channels
| Channel | Purpose | Target | Rules |
|---------|---------|---------|-------|
| Email | Official communication, records required | All | Reply within 24 hours |
| Slack/Teams | Daily communication, questions | Dev team | Response during business hours |
| Meetings | Decision making, complex discussions | Stakeholders | Agenda sent in advance |
| Portal Site | Information sharing, document management | All | Weekly updates |
| Phone | Emergency contact | Key persons | Emergency use only |

## 4. Stakeholder Expectation Management

### 4.1 Expectation Clarification
| Stakeholder | Key Expectations | Success Criteria | Measurement Method | Risks |
|-------------|------------------|------------------|-------------------|-------|
| [Stakeholder 1] | [Expectations] | [Specific Criteria] | [Measurement Method] | [Risks] |
| [Stakeholder 2] | [Expectations] | [Specific Criteria] | [Measurement Method] | [Risks] |

### 4.2 Conflict Resolution
| Conflict | Parties | Conflict Details | Resolution Approach | Decision Maker |
|----------|---------|------------------|-------------------|----------------|
| [Conflict 1] | [Party A] vs [Party B] | [Details] | [Approach] | [Decision Maker] |
| [Conflict 2] | [Party C] vs [Party D] | [Details] | [Approach] | [Decision Maker] |

## 5. Escalation Path

### 5.1 Escalation Matrix
| Issue Level | Issue Type | Initial Handler | Escalation To | Response Time |
|-------------|------------|-----------------|---------------|---------------|
| Level 1 (Minor) | Daily technical issues | Dev Team | Team Lead | Within 4 hours |
| Level 2 (Moderate) | Specification interpretation | Team Lead | Product Owner | Within 1 business day |
| Level 3 (Major) | Schedule delay risk | Project Manager | Steering Committee | Immediate |
| Level 4 (Critical) | Project cancellation risk | Steering Committee | Executive Board | Immediate |

### 5.2 Escalation Flow
````mermaid
flowchart TD
    A[Issue Occurs] --> B{Issue Level Assessment}
    B -->|Level 1| C[Team Resolution]
    B -->|Level 2| D[PM/PO Decision]
    B -->|Level 3| E[Steering Committee]
    B -->|Level 4| F[Executive Decision]
    
    C --> G[Resolved & Recorded]
    D --> H{Resolvable?}
    H -->|Yes| G
    H -->|No| E
    E --> I{Resolvable?}
    I -->|Yes| G
    I -->|No| F
    F --> J[Strategic Decision]
````

## 6. Stakeholder Satisfaction Management

### 6.1 Satisfaction Measurement Plan
| Stakeholder | Measurement Method | Frequency | Target Value | Responsible |
|-------------|-------------------|-----------|--------------|-------------|
| Project Sponsor | 1-on-1 Meeting | Monthly | Satisfaction 4+/5 | PM |
| User Representative | Survey | Quarterly | NPS +30 or higher | PO |
| Development Team | Pulse Survey | Bi-weekly | Engagement 70%+ | Scrum Master |

### 6.2 Improvement Actions
| Issue | Target Stakeholder | Improvement | Deadline | Effect Measurement |
|-------|-------------------|-------------|----------|-------------------|
| [Issue 1] | [Target] | [Improvement] | [Deadline] | [Measurement Method] |

## 7. Cultural Considerations and Diversity

### 7.1 Cultural Considerations
| Stakeholder | Cultural Background | Considerations | Communication Notes |
|-------------|-------------------|----------------|-------------------|
| [Overseas Office] | [Culture] | [Time zones, holidays] | [Language, communication style] |
| [Various Departments] | [Organizational culture] | [Decision-making process] | [Technical terminology differences] |

### 7.2 Accessibility Considerations
| Consideration | Target | Approach |
|---------------|---------|----------|
| Language | Non-native speakers | English versions of key documents |
| Time zones | Remote workers | Recording, asynchronous communication |
| Tools | Various IT literacy levels | Multiple channels provided |

## 8. Completion Checklist

### 8.1 Stakeholder Identification
- [ ] All direct stakeholders are identified
- [ ] Indirect stakeholders are considered
- [ ] External stakeholders (vendors, regulators, etc.) are included
- [ ] Stakeholder roles and responsibilities are clearly defined
- [ ] Authority levels for each stakeholder are clear

### 8.2 Engagement Planning
- [ ] Each stakeholder's expectations are documented
- [ ] Concerns and risks are identified
- [ ] Communication plan is detailed
- [ ] Escalation path is clearly defined
- [ ] Cultural considerations are addressed

### 8.3 Management Structure
- [ ] Stakeholder map is created
- [ ] Power/interest analysis is complete
- [ ] Engagement strategy is developed
- [ ] Satisfaction measurement plan is defined
- [ ] Conflict resolution approach is clear

### 8.4 Execution Readiness
- [ ] Contact information is current
- [ ] Communication tools are prepared
- [ ] Initial communication is planned
- [ ] Stakeholder register is created

## 9. Approval

### 9.1 Approval Record
| Role | Name | Approval Date | Signature |
|------|------|---------------|-----------|
| Project Manager | | | |
| Product Owner | | | |
| Project Sponsor Representative | | | |

### 9.2 Distribution
- [ ] Distributed to all stakeholders
- [ ] Posted on project portal
- [ ] Registered in change management process

## 10. Appendix

### 10.1 Stakeholder Register Template
| ID | Name | Organization | Position | Role | Email | Phone | Preferred Contact | Notes |
|----|------|--------------|----------|------|-------|-------|------------------|-------|
| | | | | | | | | |

### 10.2 RACI Chart
| Activity/Deliverable | Sponsor | PM | PO | Dev | QA | Ops |
|---------------------|---------|----|----|-----|----|----|
| Project Charter | A | R | C | I | I | I |
| Requirements Definition | I | C | R | C | C | C |
| Design Approval | I | A | R | R | C | C |
| Implementation | I | I | C | R | I | I |
| Testing | I | I | A | C | R | C |
| Release Decision | A | R | R | C | R | R |

*R: Responsible, A: Accountable, C: Consulted, I: Informed*

### 10.3 Revision History
| Version | Revision Date | Revision Content | Revised By |
|---------|---------------|------------------|------------|
| 1.0 | YYYY-MM-DD | Initial Creation | [Author] |
| | | | |