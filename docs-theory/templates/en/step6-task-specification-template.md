---
purpose: Individual task specification template
category: task_management
target_user: developer
usage_phase: step6
related_templates:
  - step3-class-design-template
  - step6-task-list-template
  - step6-todo-list-template
---

# TSK-XXX Task Specification

## Metadata
| Item | Content |
|------|---------|
| Document ID | SPEC-TSK-XXX |
| Task ID | TSK-XXX-[Layer]-[FileName] |
| Version | 1.0 |
| Created Date | YYYY-MM-DD |
| Last Updated | YYYY-MM-DD |
| Status | Draft/Under Review/Approved |
| Author | [Author Name] |
| Reviewer | [Reviewer Name] |
| Approver | [Approver Name] |
| Related Documents | CLASS-001 (Class Design Table) |
| Change History | 1.0: Initial creation (YYYY-MM-DD) |

## 1. Task Overview

### 1.1 Basic Information
| Item | Content |
|------|---------|
| Implementation Target | [ClassName] Entity Class |
| File Path | src/[layer]/[filename].ts |
| Responsibility | [Description of responsibility] |
| Estimated Time | Xh |

### 1.2 Implementation Specification
#### Class Definition
```typescript
export class [ClassName] {
  private readonly id: [IDType];
  private name: [NameType];
  private createdAt: Date;
  private updatedAt: Date;

  constructor(
    id: [IDType],
    name: [NameType]
  ) {
    this.id = id;
    this.name = name;
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  // Getters and Setters
  getId(): [IDType] { return this.id; }
  getName(): [NameType] { return this.name; }
  
  // Business Logic
  updateName(name: [NameType]): void;
  isActive(): boolean;
}
```

#### Value Objects
```typescript
export class [IDType] {
  constructor(private readonly value: string) {
    if (!value || value.length === 0) {
      throw new Error('[IDType] cannot be empty');
    }
  }
  
  getValue(): string { return this.value; }
  equals(other: [IDType]): boolean { return this.value === other.value; }
}

export class [NameType] {
  constructor(private readonly value: string) {
    if (!value || value.length < 2 || value.length > 50) {
      throw new Error('[NameType] must be between 2 and 50 characters');
    }
  }
  
  getValue(): string { return this.value; }
}
```

## 2. Test Requirements

### 2.1 Test Case List
| Test Case ID | Test Aspect | Input | Expected Result |
|--------------|-------------|-------|-----------------|
| TC-001 | Normal Case - Object Creation | Valid values | Object created successfully |
| TC-002 | Error Case - Invalid ID | Empty string | Error thrown |
| TC-003 | Error Case - Invalid Name | 1 character | Error thrown |
| TC-004 | Boundary Value - Minimum Name | 2 characters | Normal creation |
| TC-005 | Boundary Value - Maximum Name | 50 characters | Normal creation |

### 2.2 Test Implementation Example
```typescript
describe('[ClassName]', () => {
  describe('constructor', () => {
    it('should create object with valid parameters', () => {
      // Arrange
      const id = new [IDType]('[TestID]');
      const name = new [NameType]('[TestName]');

      // Act
      const obj = new [ClassName](id, name);

      // Assert
      expect(obj.getId()).toEqual(id);
      expect(obj.getName()).toEqual(name);
    });
  });

  describe('updateName', () => {
    it('should update name successfully', () => {
      // Arrange
      const obj = createTestObject();
      const newName = new [NameType]('[NewName]');

      // Act
      obj.updateName(newName);

      // Assert
      expect(obj.getName()).toEqual(newName);
    });
  });
});
```

## 3. Implementation Checklist

### 3.1 Design Compliance
- [ ] Follows domain-driven design principles
- [ ] Invariants are properly protected
- [ ] Value objects are properly implemented
- [ ] Business rules are included in the entity

### 3.2 Code Quality
- [ ] TypeScript type definitions are appropriate
- [ ] Error handling is implemented
- [ ] Follows naming conventions
- [ ] Comments are properly written

### 3.3 Test Quality
- [ ] Unit test coverage ≥90%
- [ ] Covers normal, error, and boundary value cases
- [ ] Test code is maintainable
- [ ] Mocks are used appropriately

## 4. Completion Checklist
- [ ] All methods implemented
- [ ] Unit tests implemented
- [ ] Test coverage ≥90% achieved
- [ ] Coding standards compliance
- [ ] Review completed
- [ ] Documentation updated