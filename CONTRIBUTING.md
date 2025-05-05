# Contributing Guidelines

This document outlines the key development guidelines and best practices for this project.

## Development Workflow

### Server Management
- Always kill existing related servers before starting a new one for testing
- After making changes, start up a new server for testing

### Code Organization
- Keep files under 200-300 lines of code; refactor when exceeding this limit
- Keep the codebase clean and organized
- Avoid writing one-off scripts in source files

### Development Approach
- Prefer simple solutions
- Focus on areas of code relevant to the task
- Do not touch code unrelated to the task
- Write thorough tests for all major functionality

### Code Reuse and Patterns
- Look for existing code to iterate on before creating new code
- Avoid code duplication by checking for similar existing functionality
- Do not drastically change existing patterns without explicit instruction
- When fixing issues, exhaust existing implementation options before introducing new patterns
- Remove old implementations when introducing new patterns to avoid duplicate logic

### Environment Handling
- Write code that accounts for different environments: dev, test, and prod
- Never mock data for dev or prod environments (mocking is for tests only)
- Never add stubbing or fake data patterns affecting dev or prod environments
- Never overwrite .env files without explicit confirmation

### Change Management
- Be careful to only make well-understood, related changes
- Always consider what other methods and areas might be affected by changes
- Avoid major changes to working features unless explicitly instructed
