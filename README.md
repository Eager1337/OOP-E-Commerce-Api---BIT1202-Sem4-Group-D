# E-Commerce Inventory API

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade REST API built with **FastAPI** for e-commerce inventory management. This project demonstrates industry-standard practices including OAuth2 + JWT authentication, role-based access control, async database operations with SQLAlchemy, and comprehensive API documentation.

## SDG Alignment

This project supports **SDG 8: Decent Work and Economic Growth** by providing digital infrastructure for local Sierra Leonean businesses to manage inventory, process orders, and grow their economic opportunities in the digital economy.

## Features

- **Authentication & Authorization**: OAuth2 password flow with JWT tokens and role-based access control (Admin, Manager, Customer)
- **Products**: Full CRUD with stock management, low-stock alerts, and category associations
- **Categories**: Product categorization with slug-based URLs
- **Orders**: Order processing with automatic stock deduction and status tracking
- **Reviews**: Customer feedback with rating system
- **Users**: Complete user management with admin controls
- **Statistics**: Inventory and sales analytics endpoints
- **Async Operations**: Demonstrates async/await for I/O-bound tasks
- **Auto Documentation**: Interactive Swagger UI (`/docs`) and ReDoc (`/redoc`)

## Tech Stack

| Technology | Purpose |
|------------|---------|
| FastAPI | Web framework |
| SQLAlchemy 2.0 | Async ORM |
| PostgreSQL + asyncpg | Database |
| Pydantic | Data validation |
| python-jose | JWT handling |
| passlib | Password hashing |
| Uvicorn | ASGI server |

## Project Structure

```
ecommerce_inventory_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── config.py            # Pydantic settings
│   ├── database.py          # Async DB engine & DI
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth.py              # JWT & OAuth2 authentication
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Login & registration
│       ├── users.py         # User management (Admin)
│       ├── categories.py    # Category CRUD
│       ├── products.py      # Product CRUD + stats
│       ├── orders.py        # Order processing
│       └── reviews.py       # Product reviews
├── .env.example             # Environment template
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce_inventory_api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or: venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env to set your PostgreSQL connection string
   # Example: DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/ecommerce_db
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/v1/auth/register` | Register new user | Public |
| POST | `/api/v1/auth/login` | Login (OAuth2) | Public |
| GET | `/api/v1/auth/me` | Get current user | Authenticated |

### Users (Admin Only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/` | List all users |
| GET | `/api/v1/users/{id}` | Get user by ID |
| PUT | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Delete user |

### Categories
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/v1/categories/` | Create category | Manager+ |
| GET | `/api/v1/categories/` | List categories | Public |
| GET | `/api/v1/categories/{id}` | Get category | Public |
| PUT | `/api/v1/categories/{id}` | Update category | Manager+ |
| DELETE | `/api/v1/categories/{id}` | Delete category | Manager+ |

### Products
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/v1/products/` | Create product | Manager+ |
| GET | `/api/v1/products/` | List products | Public |
| GET | `/api/v1/products/{id}` | Get product | Public |
| PUT | `/api/v1/products/{id}` | Update product | Manager+ |
| DELETE | `/api/v1/products/{id}` | Delete product | Manager+ |
| GET | `/api/v1/products/stats/inventory` | Inventory stats | Manager+ |

### Orders
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/v1/orders/` | Create order | Authenticated |
| GET | `/api/v1/orders/` | List orders | Authenticated |
| GET | `/api/v1/orders/{id}` | Get order | Authenticated |
| PUT | `/api/v1/orders/{id}` | Update status | Manager+ |
| DELETE | `/api/v1/orders/{id}` | Delete order | Manager+ |
| GET | `/api/v1/orders/stats/sales` | Sales stats | Manager+ |

### Reviews
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/v1/reviews/` | Create review | Authenticated |
| GET | `/api/v1/reviews/` | List reviews | Public |
| GET | `/api/v1/reviews/{id}` | Get review | Public |
| PUT | `/api/v1/reviews/{id}` | Update review | Owner/Admin |
| DELETE | `/api/v1/reviews/{id}` | Delete review | Owner/Admin |

## Authentication

This API uses **OAuth2 Password Flow** with JWT tokens.

1. Obtain token via `/api/v1/auth/login` (form data: username + password)
2. Include token in header: `Authorization: Bearer <token>`
3. Role-based access: Admin (full), Manager (CRUD), Customer (limited)

## Design Choices

### 1. Async Architecture
All database operations use SQLAlchemy 2.0 async patterns with `asyncpg` driver. This allows handling multiple concurrent requests efficiently without blocking the event loop.

### 2. Dependency Injection
Database sessions are injected via `Depends(get_db)`, ensuring proper session lifecycle management (commit/rollback/close) and testability.

### 3. Layered Architecture
- **Routers**: Handle HTTP requests/responses
- **Schemas**: Validate and serialize data
- **Models**: Define database structure
- **Auth**: Centralized security logic
- **Config**: Environment-based settings

### 4. Type Safety
Full Python type hints throughout the codebase, enabling IDE autocomplete and static analysis with mypy.

### 5. Security
- Passwords hashed with bcrypt
- JWT tokens with configurable expiration
- Role-based access control (RBAC)
- SQL injection prevention via ORM
- Input validation via Pydantic

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Async database relationships | Used `selectinload` for eager loading in async context |
| Decimal precision | Used `Numeric` type in SQLAlchemy and `Decimal` in Pydantic |
| Token expiration | Configured `ACCESS_TOKEN_EXPIRE_MINUTES` in settings |
| Stock management | Implemented atomic stock deduction during order creation |
| Role hierarchy | Created `require_role()` factory with numeric hierarchy levels |

## License

This project is licensed under the MIT License - see the repository for details.

## Contributors

- Group Members: [Your Names]
- Lecturer: Amandus Benjamin Coker
- Institution: Limkokwing University of Creative Technology, Sierra Leone
