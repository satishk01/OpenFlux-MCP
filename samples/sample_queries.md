# Sample Queries for OpenFlux

This document provides sample queries you can use to test OpenFlux with different types of repositories.

## General Code Exploration

### Architecture and Structure
- "What is the overall architecture of this project?"
- "Show me the main entry points of the application"
- "What are the key components and how do they interact?"
- "Explain the directory structure and organization"

### API and Interfaces
- "Find all API endpoints in this repository"
- "Show me the public interfaces and their methods"
- "What REST APIs are exposed by this service?"
- "Find GraphQL schema definitions"

### Configuration and Setup
- "How is this application configured?"
- "Show me environment variables and configuration files"
- "What are the deployment requirements?"
- "Find Docker or containerization setup"

## Language-Specific Queries

### Python Projects
- "Find all Flask or Django routes"
- "Show me database models and schemas"
- "What testing frameworks are used?"
- "Find async/await patterns in the code"
- "Show me error handling and exception classes"

### JavaScript/TypeScript Projects
- "Find React components and their props"
- "Show me Express.js middleware functions"
- "What state management is used (Redux, Context, etc.)?"
- "Find TypeScript interfaces and types"
- "Show me async functions and Promise handling"

### Java Projects
- "Find Spring Boot controllers and endpoints"
- "Show me JPA entities and repositories"
- "What design patterns are implemented?"
- "Find unit tests and test configurations"
- "Show me dependency injection setup"

### Go Projects
- "Find HTTP handlers and routes"
- "Show me struct definitions and interfaces"
- "What concurrency patterns are used?"
- "Find error handling patterns"
- "Show me package organization"

## Security and Quality

### Security Analysis
- "Find authentication and authorization code"
- "Show me input validation and sanitization"
- "What security middleware is implemented?"
- "Find password hashing and encryption"
- "Show me CORS and security headers setup"

### Code Quality
- "Find code that might need refactoring"
- "Show me complex functions that could be simplified"
- "What linting and formatting tools are configured?"
- "Find TODO comments and technical debt"
- "Show me performance optimization opportunities"

## Testing and Documentation

### Testing
- "What testing strategies are implemented?"
- "Find unit tests for core functionality"
- "Show me integration and end-to-end tests"
- "What mocking and stubbing is used?"
- "Find test coverage configuration"

### Documentation
- "Find README files and documentation"
- "Show me code comments and docstrings"
- "What API documentation is available?"
- "Find examples and usage guides"

## Sample Repositories to Try

### Small Projects (Good for Testing)
```
Repository: "microsoft/calculator"
Sample Query: "How does the calculator handle mathematical operations?"

Repository: "github/gitignore"
Sample Query: "Show me gitignore templates for Python projects"

Repository: "sindresorhus/awesome"
Sample Query: "What categories of awesome lists are available?"
```

### Medium Projects
```
Repository: "fastapi/fastapi"
Sample Queries:
- "How does FastAPI handle request validation?"
- "Show me dependency injection patterns"
- "Find async route handlers and middleware"

Repository: "expressjs/express"
Sample Queries:
- "How does Express handle middleware chaining?"
- "Show me routing implementation"
- "Find error handling mechanisms"

Repository: "spring-projects/spring-boot"
Sample Queries:
- "How does Spring Boot auto-configuration work?"
- "Show me starter project templates"
- "Find annotation processing code"
```

### Large Projects (Advanced Testing)
```
Repository: "microsoft/vscode"
Sample Queries:
- "How does VS Code handle extensions?"
- "Show me the editor core functionality"
- "Find language server protocol implementation"

Repository: "facebook/react"
Sample Queries:
- "How does React's reconciliation algorithm work?"
- "Show me hook implementations"
- "Find component lifecycle methods"

Repository: "kubernetes/kubernetes"
Sample Queries:
- "How does the scheduler assign pods to nodes?"
- "Show me API server authentication"
- "Find controller reconciliation loops"
```

## Advanced Search Patterns

### Code Pattern Searches
- "Find all functions that return promises or futures"
- "Show me singleton pattern implementations"
- "Find observer or pub/sub patterns"
- "Show me factory or builder patterns"
- "Find dependency injection containers"

### Performance and Optimization
- "Find database queries that might be slow"
- "Show me caching implementations"
- "Find memory allocation patterns"
- "Show me concurrent or parallel processing"
- "Find performance monitoring code"

### Integration Patterns
- "How does this service integrate with external APIs?"
- "Show me message queue or event handling"
- "Find database connection and ORM usage"
- "Show me logging and monitoring setup"
- "Find configuration management patterns"

## Tips for Effective Queries

1. **Be Specific**: Instead of "find functions", try "find authentication functions"
2. **Use Context**: "Show me how user registration works" vs "find user code"
3. **Ask for Patterns**: "What design patterns are used?" helps understand architecture
4. **Focus on Functionality**: "How does error handling work?" vs "find error code"
5. **Request Examples**: "Show me examples of API usage" provides concrete understanding

## Query Templates

### Understanding New Codebases
1. "What is this project and what does it do?"
2. "How do I set up and run this project locally?"
3. "What are the main features and capabilities?"
4. "How is the code organized and structured?"
5. "What technologies and frameworks are used?"

### Contributing to Projects
1. "How do I contribute to this project?"
2. "What coding standards and conventions are followed?"
3. "How do I run tests and ensure quality?"
4. "What areas of the code need improvement?"
5. "How do I submit changes and get them reviewed?"

### Debugging and Troubleshooting
1. "How does error handling work in this system?"
2. "What logging and debugging tools are available?"
3. "How do I trace through the execution flow?"
4. "What are common issues and their solutions?"
5. "How do I monitor and profile performance?"