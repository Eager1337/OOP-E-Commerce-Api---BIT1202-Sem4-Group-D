# E-Commerce Inventory API - Design Report

**Course:** PROG315 - Object-Oriented Programming 2  
**Project:** FastAPI Industry-Standard Application  
**Domain:** E-Commerce Inventory API  
**SDG Alignment:** Goal 8 - Decent Work and Economic Growth  
**Institution:** Limkokwing University of Creative Technology, Sierra Leone  
**Date:** June 2026

---

## 1. Introduction

This report documents the design and implementation of an E-Commerce Inventory API built with FastAPI, following industry-standard practices and digital public goods principles. The API provides comprehensive inventory management, order processing, and user authentication for e-commerce platforms, with particular relevance to supporting local businesses in Sierra Leone.

## 2. Design Choices

### 2.1 Framework Selection: FastAPI

FastAPI was chosen as the primary framework for several reasons:
- **Performance**: Built on Starlette and Pydantic, offering high performance comparable to Node.js and Go
- **Type Safety**: Native Python type hints enable automatic validation and serialization
- **Auto Documentation**: Generates Swagger UI and ReDoc automatically from type hints
- **Async Support**: First-class async/await support for I/O-bound operations
- **Dependency Injection**: Built-in DI system for clean, testable code

### 2.2 Database: PostgreSQL with SQLAlchemy Async ORM

PostgreSQL was selected for its robustness and ACID compliance. SQLAlchemy 2.0 provides:
- **Async Operations**: Full async support via `asyncpg` driver
- **Type Safety**: 2.0 syntax with proper type annotations
- **Relationship Management**: Declarative models with lazy/eager loading
- **Migration Support**: Alembic integration for schema versioning

### 2.3 Authentication: OAuth2 + JWT

The security architecture implements:
- **OAuth2 Password Flow**: Standardized token endpoint using form data
- **JWT Tokens**: Stateless authentication with configurable expiration
- **bcrypt Hashing**: Industry-standard password storage
- **Role-Based Access Control**: Three-tier hierarchy (Admin > Manager > Customer)

### 2.4 Architecture Pattern

The project follows a layered architecture:
```
HTTP Request → Router → Schema Validation → Auth Check → Database → Response
```

- **Routers** (`routers/`): Handle HTTP methods and status codes
- **Schemas** (`schemas.py`): Pydantic models for request/response validation
- **Models** (`models.py`): SQLAlchemy ORM entities with relationships
- **Auth** (`auth.py`): Centralized security and permission logic
- **Config** (`config.py`): Environment-based settings with Pydantic

## 3. SDG Alignment: Goal 8

### 3.1 Target 8.3: Promote Development-Oriented Policies

This API directly supports SDG 8 by:
- **Digital Infrastructure**: Provides inventory management tools for local businesses
- **Economic Growth**: Enables small businesses to scale operations efficiently
- **Employment**: Creates opportunities for youth in technology and e-commerce sectors
- **Formalization**: Helps informal sector businesses transition to formal digital operations

### 3.2 Sierra Leone Context

In Sierra Leone, many small businesses rely on manual record-keeping. This API:
- Reduces inventory waste through accurate stock tracking
- Enables data-driven business decisions via analytics endpoints
- Lowers barriers to digital commerce adoption
- Supports the government's digital transformation agenda

## 4. Challenges and Solutions

### 4.1 Async Database Relationships

**Challenge**: SQLAlchemy async mode requires careful handling of relationships to avoid lazy loading errors.

**Solution**: Used `selectinload()` for eager loading of related objects in async queries, ensuring all data is fetched within the async session scope.

### 4.2 Decimal Precision for Currency

**Challenge**: Floating-point arithmetic is unsuitable for financial calculations.

**Solution**: Implemented `Numeric(10,2)` in SQLAlchemy models and `Decimal` in Pydantic schemas, ensuring exact precision for prices and totals.

### 4.3 Role-Based Access Control

**Challenge**: Implementing flexible permission checks without code duplication.

**Solution**: Created a `require_role()` factory function that generates dependencies based on a role hierarchy (Customer=1, Manager=2, Admin=3), allowing clean decorator usage.

### 4.4 Stock Management During Orders

**Challenge**: Preventing race conditions when multiple users order the same product.

**Solution**: Implemented atomic stock deduction during order creation with immediate quantity validation, ensuring inventory accuracy.

## 5. Industry Standards Compliance

| Standard | Implementation |
|----------|---------------|
| RESTful Design | Predictable endpoints (`/items/{id}`), proper HTTP methods |
| HTTP Methods | GET (read), POST (create), PUT (update), DELETE (remove) |
| Status Codes | 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found |
| Security | Password hashing, JWT tokens, RBAC, input validation |
| Documentation | Swagger UI (`/docs`) and ReDoc (`/redoc`) auto-generated |
| Open Source | MIT License, GitHub repository with README |
| Type Safety | Full Python type hints throughout codebase |

## 6. Conclusion

This E-Commerce Inventory API demonstrates the application of object-oriented programming principles in a real-world context. Through FastAPI's dependency injection, SQLAlchemy's ORM patterns, and Pydantic\s data validation, the project achieves clean separation of concerns and maintainable code. The alignment with SDG 8 ensures the project contributes meaningfully to Sierra Leone's economic development while meeting all academic requirements for industry-standard practices.

---

**Font:** Tahoma, Size 10, Line Spacing 1.15, Justified  
*(Format this document according to submission requirements when printing)*
