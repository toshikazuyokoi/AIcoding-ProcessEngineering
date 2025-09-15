---
purpose: Directory structure map template
category: implementation
target_user: developer
usage_phase: step5
related_templates:
  - step2-tech-stack-template
  - step5-components-template
---

# Directory Structure Map

## Metadata
| Item | Content |
|------|---------|
| Document ID | DIR-001 |
| Version | 1.0 |
| Created Date | YYYY-MM-DD |
| Last Updated | YYYY-MM-DD |
| Status | Draft/Under Review/Approved |
| Author | [Author Name] |
| Reviewer | [Reviewer Name] |
| Approver | [Approver Name] |
| Related Documents | TECH-001 (Technology Stack Selection), COMP-001 (Implementation Components List) |
| Change History | 1.0: Initial creation (YYYY-MM-DD) |

## 1. Overall Project Structure

```
project-root/
├── README.md                          # Project overview
├── package.json                       # Dependency definitions
├── tsconfig.json                      # TypeScript configuration
├── .env.example                       # Environment variable template
├── docker-compose.yml                 # Development environment definition
├── .github/                           # GitHub configuration
│   └── workflows/                     # CI/CD workflows
│       ├── test.yml                   # Test execution
│       ├── build.yml                  # Build and deploy
│       └── security.yml               # Security scan
├── docs/                              # Project documentation
│   ├── api/                           # API specifications
│   ├── architecture/                  # Architecture documents
│   └── deployment/                    # Deployment procedures
├── src/                               # Source code
│   ├── presentation/                  # Presentation layer
│   │   ├── controllers/               # REST API controllers
│   │   ├── dto/                       # Data transfer objects
│   │   │   ├── request/               # Request DTOs
│   │   │   └── response/              # Response DTOs
│   │   ├── middleware/                # Middleware
│   │   └── validators/                # Input validation
│   ├── application/                   # Application layer
│   │   ├── services/                  # Business logic
│   │   ├── usecases/                  # Use case implementations
│   │   └── interfaces/                # Application interfaces
│   ├── domain/                        # Domain layer
│   │   ├── entities/                  # Entities
│   │   ├── repositories/              # Repository interfaces
│   │   ├── services/                  # Domain services
│   │   └── value-objects/             # Value objects
│   ├── infrastructure/                # Infrastructure layer
│   │   ├── database/                  # Database implementation
│   │   │   ├── repositories/          # Repository implementations
│   │   │   ├── migrations/            # Migrations
│   │   │   └── seeds/                 # Seed data
│   │   ├── external/                  # External API integration
│   │   ├── config/                    # Configuration management
│   │   └── logging/                   # Log management
│   ├── shared/                        # Common modules
│   │   ├── constants/                 # Constant definitions
│   │   ├── enums/                     # Enumerations
│   │   ├── types/                     # Type definitions
│   │   ├── utils/                     # Utilities
│   │   └── exceptions/                # Exception classes
│   └── main.ts                        # Application entry point
├── tests/                             # Test code
│   ├── unit/                          # Unit tests
│   │   ├── controllers/               # Controller tests
│   │   ├── services/                  # Service tests
│   │   ├── repositories/              # Repository tests
│   │   └── utils/                     # Utility tests
│   ├── integration/                   # Integration tests
│   │   ├── api/                       # API integration tests
│   │   ├── database/                  # DB integration tests
│   │   └── external/                  # External integration tests
│   ├── e2e/                           # E2E tests
│   │   ├── scenarios/                 # Test scenarios
│   │   ├── fixtures/                  # Test data
│   │   └── helpers/                   # Test helpers
│   └── performance/                   # Performance tests
├── scripts/                           # Operational scripts
│   ├── build.sh                       # Build script
│   ├── deploy.sh                      # Deployment script
│   ├── backup.sh                      # Backup script
│   └── migration.sh                   # Migration script
└── dist/                              # Build artifacts (not in Git)
```

## 2. Naming Conventions

### 2.1 File Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Class | PascalCase + suffix | UserController.ts |
| Interface | I + PascalCase | IUserRepository.ts |
| DTO | PascalCase + Request/Response | UserCreateRequest.ts |
| Test | Target filename + .spec.ts | UserService.spec.ts |
| Configuration | kebab-case | database.config.ts |

### 2.2 Directory Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Multiple words | kebab-case | detailed-design |
| Singular | Entity-related | entity, service |
| Plural | Collections | controllers, repositories |

### 2.3 Package Structure
| Package | Purpose | Naming Convention |
|---------|---------|-------------------|
| @/presentation | Presentation layer | PascalCase |
| @/application | Application layer | PascalCase |
| @/domain | Domain layer | PascalCase |
| @/infrastructure | Infrastructure layer | PascalCase |
| @/shared | Common modules | PascalCase |

## 3. Import Rules

### 3.1 Import Order
```typescript
// 1. External libraries (Node.js standard → third-party)
import { Controller, Get, Post, Body } from '@nestjs/common';
import { Repository } from 'typeorm';
import express from 'express';

// 2. Internal modules (no relative paths, use absolute paths)
import { UserService } from '@/application/services/UserService';
import { User } from '@/domain/entities/User';
import { IUserRepository } from '@/domain/repositories/IUserRepository';

// 3. Type definitions (type-only import)
import type { UserCreateRequest } from '@/presentation/dto/request/UserCreateRequest';
import type { UserResponse } from '@/presentation/dto/response/UserResponse';

// 4. Configuration and constants
import { DATABASE_CONFIG } from '@/infrastructure/config/database.config';
import { HTTP_STATUS } from '@/shared/constants/http-status';
```

### 3.2 Path Alias Configuration
```json
{
  "compilerOptions": {
    "baseUrl": "./src",
    "paths": {
      "@/*": ["*"],
      "@/presentation/*": ["presentation/*"],
      "@/application/*": ["application/*"],
      "@/domain/*": ["domain/*"],
      "@/infrastructure/*": ["infrastructure/*"],
      "@/shared/*": ["shared/*"],
      "@/tests/*": ["../tests/*"]
    }
  }
}
```

## 4. Completion Checklist
- [ ] Directory structure is properly designed
- [ ] Naming conventions are unified
- [ ] Import rules are clearly defined
- [ ] Path aliases are properly configured