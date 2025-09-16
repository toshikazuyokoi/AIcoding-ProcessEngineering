# Test Case Definition Document

## Metadata
- **Purpose**: Define comprehensive test cases for quality assurance
- **Category**: Test Design
- **Target User**: QA Engineer, Test Engineer, Development Team
- **Usage Phase**: Step 4 - Test Design
- **Related Templates**: 
  - step4-test-targets-template.md
  - step4-test-strategy-template.md
  - step3-interfaces-template.md

| Item | Content |
|------|---------|
| Document ID | [STEP4-CASE-001] |
| Version | [v1.0] |
| Created Date | [YYYY-MM-DD] |
| Last Updated | [YYYY-MM-DD] |
| Status | [Draft/Under Review/Approved/Deprecated] |
| Author | [Author Name] |
| Approver | [Approver Name (if Status is Approved)] |
| Tags | #step4-test-design #test-cases #quality-assurance |
| Related Documents | [[TARGET-001](./step4-test-targets-template.md)] [[STRATEGY-001](./step4-test-strategy-template.md)] |
| Change History | [v1.0] YYYY-MM-DD: Initial version created<br>[v1.1] YYYY-MM-DD: Added E2E test cases (TC-201 to TC-205) |

## 1. Unit Test Cases

### TC-001: QueryController.handleQuery - Normal Case

#### Basic Information
| Item | Content |
|------|---------|
| Test Case ID | TC-001 |
| Target Method | QueryController.handleQuery |
| Test Perspective | Normal case - Valid query |
| Priority | High |

#### Test Conditions
| Item | Content |
|------|---------|
| Preconditions | System is running normally |
| Input Data | { query: "Hello, world!" } |
| Expected Result | Normal response is returned |
| Postconditions | Logs are output normally |

#### Test Steps
1. Create test Request object
2. Call handleQuery method
3. Verify return value
4. Confirm log output

#### Implementation Example
```typescript
describe('QueryController.handleQuery', () => {
  it('should return valid response for valid query', async () => {
    // Arrange
    const mockRequest = {
      body: { query: 'Hello, world!' }
    };
    const expectedResponse = {
      status: 200,
      data: 'Processed: Hello, world!'
    };

    // Act
    const result = await controller.handleQuery(mockRequest);

    // Assert
    expect(result).toEqual(expectedResponse);
    expect(mockLogger.info).toHaveBeenCalledWith(
      'Query processed: Hello, world!'
    );
  });
});
```

### TC-002: QueryController.handleQuery - Error Case

#### Basic Information
| Item | Content |
|------|---------|
| Test Case ID | TC-002 |
| Target Method | QueryController.handleQuery |
| Test Perspective | Error case - Invalid query |
| Priority | High |

#### Test Conditions
| Item | Content |
|------|---------|
| Preconditions | System is running normally |
| Input Data | { query: "" } |
| Expected Result | ValidationError is thrown |
| Postconditions | Error log is output |

#### Implementation Example
```typescript
it('should throw ValidationError for empty query', async () => {
  // Arrange
  const mockRequest = {
    body: { query: '' }
  };

  // Act & Assert
  await expect(controller.handleQuery(mockRequest))
    .rejects.toThrow(ValidationError);
  
  expect(mockLogger.error).toHaveBeenCalledWith(
    expect.stringContaining('Query processing failed')
  );
});
```

## 2. Integration Test Cases

### TC-101: Query API - Normal Case

#### Basic Information
| Item | Content |
|------|---------|
| Test Case ID | TC-101 |
| Target API | POST /api/query |
| Test Perspective | Normal case - End-to-end |
| Priority | High |

#### Test Conditions
| Item | Content |
|------|---------|
| Preconditions | API server is running |
| Request | POST /api/query<br>{ "query": "test query" } |
| Expected Result | 200 OK<br>Normal response |
| Postconditions | Recorded in database |

#### Implementation Example
```typescript
describe('POST /api/query', () => {
  it('should process query successfully', async () => {
    // Arrange
    const queryData = { query: 'test query' };

    // Act
    const response = await request(app)
      .post('/api/query')
      .send(queryData)
      .expect(200);

    // Assert
    expect(response.body).toMatchObject({
      status: 'success',
      data: expect.any(String)
    });
  });
});
```

## 3. E2E Test Cases

### TC-201: User Query Processing Flow

#### Basic Information
| Item | Content |
|------|---------|
| Test Case ID | TC-201 |
| Scenario | User enters query and gets results |
| Test Perspective | End user experience |
| Priority | High |

#### Test Steps
1. Access application in browser
2. Enter text in query input field
3. Click submit button
4. Confirm result is displayed
5. Confirm recorded in history

#### Implementation Example (Playwright)
```typescript
test('user can submit query and get response', async ({ page }) => {
  // Navigate to application
  await page.goto('/');

  // Input query
  await page.fill('[data-testid=query-input]', 'test query');
  
  // Submit query
  await page.click('[data-testid=submit-button]');
  
  // Verify response
  await expect(page.locator('[data-testid=response]')).toBeVisible();
  await expect(page.locator('[data-testid=response]')).toContainText('test query');
  
  // Verify history
  await expect(page.locator('[data-testid=history]')).toContainText('test query');
});
```

## 4. Completion Checklist
- [ ] Unit test cases are comprehensively defined
- [ ] Integration test cases cover critical paths
- [ ] E2E test cases cover user scenarios
- [ ] Implementation examples are specifically described
- [ ] Expected results are clearly defined