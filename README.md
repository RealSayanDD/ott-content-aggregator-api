
# OTT Content Aggregator API

A RESTful API built with **FastAPI** to aggregate content from multiple Over-The-Top (OTT) streaming platforms. The application is designed to provide a centralized backend for managing and accessing streaming content, with authentication, database integration, and Redis caching.

## Features

- **REST API:** Built using FastAPI for efficient API development.
- **Database Integration:** PostgreSQL for persistent data storage.
- **ORM:** SQLAlchemy 2.0 for database operations.
- **Data Validation:** Pydantic v2 for request and response validation.
- **Authentication:** JWT-based authentication using `python-jose` and password hashing using `passlib`.
- **Caching:** Redis to cache frequently requested data and improve API response times.
- **Database Migrations:** Alembic for managing database schema changes.
- **Testing:** Pytest and HTTPX for API testing.
- **Interactive API Documentation:** Swagger UI and ReDoc.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Programming language |
| FastAPI | API framework |
| PostgreSQL | Relational database |
| SQLAlchemy 2.0 | ORM and database operations |
| Pydantic v2 | Data validation and serialization |
| python-jose | JWT token handling |
| passlib | Password hashing |
| Redis | Caching |
| Alembic | Database migrations |
| Pytest | Automated testing |
| HTTPX | HTTP client for API tests |

## Project Structure

```text
ott-aggregator-api-app/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   ├── services/
│   ├── core/
│   └── cache/
├── tests/
├── alembic/
├── alembic.ini
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

> Note: The directory structure above is a suggested layout. Adjust it to match the actual structure of your repository.

## Prerequisites

Make sure you have the following installed:

- Python 3.10 or later
- PostgreSQL
- Redis
- Git
- pip

## Getting Started

### 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd ott-aggregator-api-app
```

Replace `<YOUR_REPOSITORY_URL>` with your actual Git repository URL.

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**macOS / Linux**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root using `.env.example` as a template.

Example configuration:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/ott_db

SECRET_KEY=replace_with_a_secure_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_URL=redis://localhost:6379/0
```

Replace the sample database credentials with your local PostgreSQL credentials.

**Important:** Never commit your `.env` file, database passwords, or secret keys to GitHub.

### 5. Set Up the Database

Create a PostgreSQL database named `ott_db`, or use another name and update `DATABASE_URL` accordingly.

For example, from the PostgreSQL shell:

```sql
CREATE DATABASE ott_db;
```

### 6. Run Database Migrations

If Alembic has already been configured:

```bash
alembic upgrade head
```

If migrations have not yet been created, configure Alembic for your SQLAlchemy models before running this command.

### 7. Start Redis

Ensure your Redis server is running and that `REDIS_URL` points to the correct instance.

For a local Redis installation, the default URL is:

```text
redis://localhost:6379/0
```

### 8. Run the Application

Assuming your FastAPI application instance is located in `app/main.py` and is named `app`:

```bash
uvicorn app.main:app --reload
```

The API will generally be available at:

- **API Base URL:** http://127.0.0.1:8000
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

These URLs assume the default Uvicorn host and port.

## Redis Caching

Redis is used as an in-memory caching layer to reduce repeated database queries and improve response times for frequently accessed data.

### Caching Workflow

1. The client sends an API request.
2. The application checks Redis for the requested data.
3. If the data exists in the cache (**cache hit**), the cached response is returned.
4. If the data is absent (**cache miss**), the application retrieves it from PostgreSQL.
5. The result is stored in Redis with an appropriate expiration time (TTL).
6. Subsequent requests can retrieve the data from the cache until it expires or is invalidated.

### Benefits

- Reduced database load.
- Faster responses for repeated requests.
- Improved efficiency for read-heavy endpoints.
- Configurable cache expiration using TTL.
- Better scalability when caching is applied appropriately.

Cache keys, TTL values, and invalidation rules should be configured according to the actual API endpoints and data-update workflow.

## Running Tests

Run the automated test suite with:

```bash
pytest
```

For verbose test output:

```bash
pytest -v
```

To measure test coverage, if `pytest-cov` is installed:

```bash
pytest --cov=app
```

## API Documentation

FastAPI generates interactive API documentation automatically.

| Documentation | URL |
|---|---|
| Swagger UI | `/docs` |
| ReDoc | `/redoc` |
| OpenAPI Schema | `/openapi.json` |

Use the documentation to inspect available endpoints, request parameters, response schemas, and authentication requirements.

## Development Guidelines

- Keep database credentials and secret keys in environment variables.
- Validate incoming data using Pydantic schemas.
- Use SQLAlchemy sessions appropriately and close them after use.
- Apply database schema changes through Alembic migrations.
- Use Redis TTL and cache invalidation to prevent stale data.
- Write tests for API endpoints, authentication, database operations, and caching behavior.
- Avoid caching sensitive or user-specific responses without appropriate isolation.
- Keep dependencies and project documentation updated.

## Future Improvements

Potential enhancements include:

- Expanding integrations with multiple OTT platforms.
- Adding advanced content search and filtering.
- Implementing pagination and sorting.
- Improving cache invalidation strategies.
- Adding monitoring, logging, and performance metrics.
- Increasing automated test coverage.

## Contributors

Developed as part of a Python Development Internship project.

- **Project:** OTT Content Aggregator API
- **Backend Framework:** FastAPI
- **Caching:** Redis
- **Database:** PostgreSQL

Add contributor names and individual responsibilities here.

## License

Add the appropriate license for this project before distributing it publicly.
