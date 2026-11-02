# 🎬 OTT Content Aggregator API

<p align="center">
  <strong>A centralized REST API for discovering and aggregating OTT content across multiple streaming platforms.</strong>
  <br />
  Explore movies, TV shows, genres, and streaming availability through a unified backend service.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Redis-Caching-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy" />
  <img src="https://img.shields.io/badge/Pydantic-Validation-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic" />
</p>

---

## 📌 Overview

**OTT Content Aggregator API** is a collaborative backend development project designed to provide a centralized platform for discovering content available across different Over-The-Top (OTT) streaming services.

Instead of searching through multiple streaming platforms individually, the application aims to provide a unified API through which users can explore movies, television shows, genres, and streaming platform information.

The project focuses on building a scalable REST API with efficient database management, secure authentication, structured data validation, and optimized response times through Redis caching.

### 🎯 Project Vision

To develop an efficient OTT content aggregation system where:

* Users can discover movies and television shows from different OTT platforms.
* Content can be explored through categories, genres, and streaming platforms.
* Authenticated users can access protected API functionality.
* Database operations are handled efficiently using SQLAlchemy.
* Frequently requested data can be served through Redis caching.
* The backend follows a modular and scalable architecture.

> **Development Approach:** The project is being developed collaboratively using FastAPI, PostgreSQL, SQLAlchemy, and Redis, with separate responsibilities for database management, authentication, and caching.

---

## ✨ Key Features

### 🎥 OTT Content Aggregation

* Centralized content discovery through a REST API.
* Structured representation of movies and television shows.
* Support for organizing content by genres and streaming platforms.
* Foundation for searching and filtering OTT content.
* Unified API response structure.

### 🔐 Authentication & Authorization

* User authentication using JWT.
* Secure password hashing using Passlib.
* Token-based authentication using `python-jose`.
* Protected API endpoints.
* Authentication-related request validation.

### ⚡ Redis Caching

* Redis integration for high-performance data retrieval.
* Caching frequently requested API responses.
* Cache hit and cache miss handling.
* Configurable cache expiration using TTL (Time To Live).
* Reduced unnecessary database queries.
* Cache invalidation to maintain data consistency.
* Graceful handling of Redis availability issues.

### 🗄️ Database Management

* PostgreSQL relational database integration.
* SQLAlchemy 2.0 ORM for database operations.
* Structured database models and relationships.
* Database session management.
* Alembic for database schema migrations.

### 🛡️ API Validation

* Pydantic v2 for request and response validation.
* Structured API response models.
* Input validation and error handling.
* Consistent API data structures.

### 🧪 Testing

* Pytest-based testing framework.
* HTTPX for API endpoint testing.
* Foundation for testing authentication, database operations, and caching functionality.

---

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Backend programming language |
| FastAPI | REST API development |
| PostgreSQL | Relational database |
| SQLAlchemy 2.0 | Object Relational Mapping (ORM) |
| Pydantic v2 | Request and response validation |
| Redis | In-memory caching |
| python-jose | JWT authentication |
| Passlib | Password hashing |
| Alembic | Database migrations |
| Pytest | Automated testing |
| HTTPX | HTTP client and API testing |
| Uvicorn | ASGI application server |

---

## 🏗️ Application Architecture

The application follows a modular backend architecture that separates API routing, business logic, database operations, authentication, and caching.

### Request Processing Flow

```text
                 Client Request
                       |
                       v
                FastAPI Application
                       |
                       v
                 API Endpoint
                       |
                       v
                Business Logic
                       |
                       v
                Redis Cache Check
                       |
              +--------+--------+
              |                 |
              v                 v
          Cache Hit         Cache Miss
              |                 |
              v                 v
        Return Cached      Query PostgreSQL
             Data                |
                                 v
                          Retrieve Data
                                 |
                                 v
                          Store in Redis
                                 |
                                 v
                          Return API Response
```

### Core Components

| Component | Responsibility |
|---|---|
| FastAPI | Handles incoming HTTP requests and API routing |
| PostgreSQL | Stores application data |
| SQLAlchemy | Manages database interactions |
| Pydantic | Validates incoming and outgoing data |
| Redis | Stores frequently accessed data temporarily |
| JWT | Provides token-based authentication |
| Alembic | Manages database schema migrations |
| Pytest | Tests application functionality |

---

## 📂 Project Structure

The following represents a suggested modular structure. Adjust the filenames and directories to match the actual repository.

```text
ott-aggregator-api/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── api/
│   │   └── routes/
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   └── models.py
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │
│   ├── cache/
│   │   ├── redis.py
│   │   └── cache.py
│   │
│   └── utils/
│
├── alembic/
│
├── tests/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

### Core Modules

| Module | Responsibility |
|---|---|
| `main.py` | FastAPI application entry point |
| `api/routes/` | API endpoint definitions |
| `core/config.py` | Application configuration |
| `core/security.py` | Authentication and security utilities |
| `database/` | Database connection and ORM models |
| `schemas/` | Pydantic request and response schemas |
| `services/` | Application business logic |
| `cache/redis.py` | Redis connection management |
| `cache/cache.py` | Reusable caching operations |
| `alembic/` | Database migration management |
| `tests/` | Automated application tests |

*Note: The directory structure is illustrative and should be synchronized with the actual implementation.*

---

## ⚙️ Getting Started

Follow these instructions to set up the project locally.

### Prerequisites

Make sure you have the following installed:

* Python 3.10 or above
* PostgreSQL
* Redis
* Git
* Visual Studio Code or another code editor

Verify your installation:

```bash
python --version
pip --version
git --version
```

Verify Redis is running:

```bash
redis-cli ping
```

Expected response:

```text
PONG
```

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

### 2. Navigate to the Project

```bash
cd ott-aggregator-api
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment.

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root.

Configure the required PostgreSQL connection, Redis connection, JWT secret, and other application settings according to the project's configuration.

Example configuration:

```env
DATABASE_URL=<YOUR_POSTGRESQL_CONNECTION_STRING>

REDIS_URL=redis://localhost:6379/0

SECRET_KEY=<YOUR_SECRET_KEY>
```

*Use the actual environment variable names expected by the application. Never commit your `.env` file.*

### 6. Run Database Migrations

Apply the existing Alembic migrations:

```bash
alembic upgrade head
```

### 7. Start Redis

Make sure the Redis server is running locally.

```bash
redis-server
```

### 8. Start the FastAPI Server

For an application whose entry point is `app/main.py`:

```bash
uvicorn app.main:app --reload
```

### 9. Access API Documentation

Once the server starts, access the interactive API documentation:

**Swagger UI:**

```text
http://127.0.0.1:8000/docs
```

**ReDoc:**

```text
http://127.0.0.1:8000/redoc
```

*Note: Adjust the Uvicorn import path and setup commands if the repository uses a different application entry point.*

---

## ⚡ Redis Caching Architecture

Redis is integrated into the application to improve API performance by reducing repeated database queries.

### How Caching Works

1. A client sends a request to an API endpoint.
2. The application checks whether the requested data exists in Redis.
3. If the data exists (Cache Hit), the cached result is returned.
4. If the data does not exist (Cache Miss), the application queries PostgreSQL.
5. The retrieved result is stored in Redis with an expiration time.
6. Subsequent requests can retrieve the result directly from Redis.

### Caching Benefits

* Faster API response times for frequently accessed data.
* Reduced PostgreSQL database workload.
* Improved application scalability.
* Efficient utilization of database resources.
* Automatic cache expiration through TTL.

### Cache Management

The caching layer is designed around three fundamental operations:

| Operation | Description |
|---|---|
| GET | Retrieve cached data |
| SET | Store data with an expiration time |
| DELETE | Invalidate cached data |

> **Important:** Cache invalidation is essential whenever underlying database records are modified. It prevents outdated cached responses from being served to clients.

---

## 🔐 Security Considerations

Security is an important aspect of the backend architecture.

The application incorporates or is designed around the following security mechanisms:

* JWT-based authentication.
* Secure password hashing.
* Protected API endpoints.
* Pydantic-based input validation.
* Environment-based secret management.
* Database connection security.
* Proper authentication and authorization checks.
* Secure handling of Redis connection credentials.

> **Important:** Sensitive credentials, JWT secrets, and database passwords must never be committed to the public repository.

---

## 🧪 Testing

The project uses Pytest and HTTPX for automated testing.

Run the test suite using:

```bash
pytest
```

Run tests with detailed output:

```bash
pytest -v
```

Testing areas include:

* API endpoint functionality.
* Request and response validation.
* Authentication and authorization.
* Database operations.
* Redis caching operations.
* Cache hit and cache miss scenarios.
* Error handling.

---

## 🔭 Development Roadmap

The project is being developed incrementally, with different modules implemented collaboratively.

### Phase 1 — Project Foundation

- [x] Python backend setup
- [x] FastAPI integration
- [x] PostgreSQL technology selection
- [x] SQLAlchemy 2.0 integration
- [x] Pydantic v2 integration

### Phase 2 — Database Management

- [ ] Database model implementation
- [ ] Database relationship management
- [ ] Database session management
- [ ] Alembic migration integration
- [ ] Database testing

### Phase 3 — Authentication & Authorization

- [ ] JWT authentication
- [ ] Password hashing with Passlib
- [ ] User registration and login
- [ ] Protected API endpoints
- [ ] Authentication testing

### Phase 4 — Redis Caching

- [ ] Redis connection configuration
- [ ] Reusable caching utility functions
- [ ] Cache GET, SET, and DELETE operations
- [ ] TTL-based cache expiration
- [ ] API endpoint caching integration
- [ ] Cache invalidation
- [ ] Redis failure handling
- [ ] Cache performance testing

### Phase 5 — OTT Content Aggregation

- [ ] Content aggregation functionality
- [ ] Movie and TV show management
- [ ] Genre-based content organization
- [ ] Streaming platform integration
- [ ] Search and filtering functionality
- [ ] API response optimization

### Phase 6 — Testing & Production Readiness

- [ ] Automated API testing
- [ ] Database testing
- [ ] Authentication testing
- [ ] Redis caching testing
- [ ] Error handling and logging
- [ ] Performance optimization
- [ ] Security testing
- [ ] Deployment and monitoring

*Roadmap checkboxes should be updated according to actual implementation progress.*

---

## 🤝 Contributing

This project is being developed collaboratively as part of a Python Development Internship.

Team members work on different modules while maintaining a common codebase and development workflow.

### Development Workflow

**1. Get the latest main branch**

```bash
git checkout main
git pull origin main
```

**2. Create or switch to your feature branch**

```bash
git checkout -b feature/your-feature-name
```

**3. Make your changes and test locally**

```bash
pytest -v
```

**4. Stage and commit your changes**

```bash
git add .
git commit -m "Add your feature description"
```

**5. Push your feature branch**

```bash
git push origin feature/your-feature-name
```

**6. Create a Pull Request**

* Base branch: `main`
* Compare branch: Your feature branch
* Provide a descriptive title and summary.
* Review the changes before merging.

### Contribution Guidelines

* Keep code modular and organized.
* Follow Python coding conventions.
* Write reusable functions wherever possible.
* Test changes before submitting a pull request.
* Avoid committing unnecessary files.
* Resolve merge conflicts carefully.
* Never commit API keys, passwords, or environment files.

---

## 👥 Team Development

The OTT Content Aggregator API is a collaborative internship project involving multiple contributors.

The development responsibilities are divided across different technical areas:

| Responsibility | Focus Area |
|---|---|
| Database Development | PostgreSQL and SQLAlchemy |
| Authentication | JWT authentication and password security |
| Caching | Redis integration and API performance optimization |

Each module contributes to building a unified, efficient, and maintainable backend application.

---

## 📌 Current Project Direction

```text
FastAPI Application Setup
          |
          v
Database Integration
          |
          v
Authentication & Authorization
          |
          v
Redis Caching Integration
          |
          v
OTT Content Aggregation
          |
          v
API Testing & Optimization
          |
          v
Production-Ready Backend API
```

---

<p align="center">
  <strong>OTT Content Aggregator API</strong>
  <br />
  Building a unified OTT discovery experience through efficient backend engineering.
</p>
