
# OTT Content Aggregator API

A backend REST API built with **FastAPI** to provide a centralized platform for aggregating and accessing content from multiple Over-The-Top (OTT) streaming services.

The project focuses on building a scalable API with database integration, secure authentication, data validation, and **Redis-based caching** to improve performance and reduce repetitive database queries.

## Key Features

- **RESTful API:** Efficient API development using FastAPI.
- **Database Management:** PostgreSQL for persistent data storage.
- **ORM Integration:** SQLAlchemy 2.0 for database operations.
- **Data Validation:** Pydantic v2 for request validation and response serialization.
- **Authentication:** JWT-based authentication using `python-jose` and password hashing using `passlib`.
- **Redis Caching:** In-memory caching to reduce database load and improve response times.
- **Database Migrations:** Alembic for version-controlled schema changes.
- **Automated Testing:** Pytest and HTTPX for testing API functionality.
- **Interactive Documentation:** Automatically generated Swagger UI and ReDoc documentation.

> Note: The features above describe the intended project capabilities. Ensure each feature is implemented before presenting it as completed.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core programming language |
| FastAPI | REST API framework |
| PostgreSQL | Relational database |
| SQLAlchemy 2.0 | Database ORM |
| Pydantic v2 | Data validation and serialization |
| python-jose | JWT creation and verification |
| passlib | Password hashing |
| Redis | In-memory caching |
| Alembic | Database migrations |
| Pytest | Automated testing |
| HTTPX | HTTP client and API testing |

## Architecture Overview

The application follows a typical API architecture in which requests pass through the API layer, interact with the caching layer when appropriate, and access the database when necessary.

```text
              Client Application
                      |
                      v
                 FastAPI API
                      |
             +--------+--------+
             |                 |
             v                 v
        Redis Cache       PostgreSQL
             |                 |
             +--------+--------+
                      |
                      v
                JSON Response
```

**Request flow:**
1. The client sends an HTTP request to the API.
2. FastAPI validates the request and applies the relevant authentication and authorization checks.
3. For cacheable requests, the application checks Redis for an existing result.
4. On a cache miss, the application retrieves the required data from PostgreSQL.
5. Where appropriate, the result is cached in Redis with a configured expiration time.
6. The API returns the response to the client.

*The actual request flow depends on the endpoints and caching logic implemented in the project.*

## Project Structure

A suggested directory structure is shown below. Adapt it to match the actual repository.

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

## Getting Started

### Prerequisites

Install the following before running the application:

- Python 3.10 or later
- PostgreSQL
- Redis
- Git
- pip

### 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd ott-aggregator-api-app
```

Replace `<YOUR_REPOSITORY_URL>` with the actual repository URL.

### 2. Create and Activate a Virtual Environment

Create the environment:

```bash
python -m venv venv
```

**macOS / Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Ensure that `requirements.txt` includes the dependencies required by your implementation.

### 4. Configure Environment Variables

Create a `.env` file in the project root. Use `.env.example` as a template if it is available.

Example configuration:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/ott_db

SECRET_KEY=replace_with_a_secure_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_URL=redis://localhost:6379/0
```

Update the values according to your local configuration. The variable names must match those read by your application.

**Security:** Never commit your `.env` file, database credentials, or production secret keys to version control.

### 5. Configure PostgreSQL

Create a database for the application:

```sql
CREATE DATABASE ott_db;
```

Update `DATABASE_URL` with your PostgreSQL username, password, host, port, and database name.

### 6. Apply Database Migrations

If Alembic is configured and migration scripts are available, run:

```bash
alembic upgrade head
```

This applies the migrations required to bring the database schema to the latest revision.

### 7. Start Redis

Start your local Redis server or connect to an available Redis instance.

Default local connection URL:

```text
redis://localhost:6379/0
```

Verify that Redis is running and accessible before starting the application if Redis is a required dependency.

### 8. Run the API

Assuming the FastAPI instance is named `app` in `app/main.py`, run:

```bash
uvicorn app.main:app --reload
```

The application will be available at the following addresses when using the default Uvicorn configuration:

| Resource | URL |
|---|---|
| API base URL | http://127.0.0.1:8000 |
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| OpenAPI schema | http://127.0.0.1:8000/openapi.json |

## Redis Caching

Redis serves as an in-memory caching layer for data that is requested frequently and is suitable for caching.

### How Caching Works

**Cache hit:** The requested data is available in Redis, so the application can return it without querying PostgreSQL again.

**Cache miss:** The requested data is not in Redis, so the application retrieves it from PostgreSQL and may store the result in Redis for subsequent requests.

### Caching Workflow

1. Receive a request for cacheable data.
2. Generate a cache key based on the resource and relevant request parameters.
3. Check Redis for the cached result.
4. If the result exists, return the cached data.
5. Otherwise, query PostgreSQL and cache the result with an appropriate time-to-live (TTL).
6. Invalidate or refresh the cache when relevant data changes.

### Benefits

- Faster responses for repeated read requests.
- Fewer repetitive database queries.
- Reduced database workload.
- Configurable cache expiration using TTL.
- Improved efficiency for read-heavy workloads.

### Cache Invalidation

Caching must account for changes to the underlying data. Depending on the endpoint, the application can invalidate or refresh relevant cache entries after create, update, or delete operations.

Cache keys, TTL values, serialization, and invalidation strategies should be defined according to the application's actual data model and API behavior.

Avoid caching sensitive information or user-specific responses without appropriate access controls and cache-key isolation.

## Testing

Run the test suite using Pytest:

```bash
pytest
```

Run tests with more detailed output:

```bash
pytest -v
```

If `pytest-cov` is installed, measure test coverage with:

```bash
pytest --cov=app
```

Recommended areas to test include:

- API request and response validation.
- Database operations.
- Authentication and authorization.
- Redis cache hits and misses.
- Cache expiration and invalidation.
- Error handling when external dependencies are unavailable.

## Development Guidelines

- Keep configuration and secrets in environment variables.
- Use Pydantic schemas to validate API data.
- Manage database schema changes through Alembic.
- Handle database sessions and Redis connections safely.
- Use appropriate cache TTLs and invalidation rules.
- Write tests for new features and bug fixes.
- Document new endpoints and configuration changes.
- Keep dependencies up to date and avoid committing generated files or secrets.

## Future Enhancements

Potential areas for further development include:

- Additional OTT content integrations.
- Advanced search, filtering, and pagination.
- More comprehensive caching and invalidation strategies.
- Improved logging and performance monitoring.
- Expanded automated test coverage.
- Deployment and containerization.

## Contributors

**Project:** OTT Content Aggregator API  
**Project Type:** Python Development Internship  
**Backend Framework:** FastAPI  
**Database:** PostgreSQL  
**Caching Layer:** Redis

Add contributor names, repository links, and individual responsibilities here.

## License

Specify the appropriate license for this project before distributing it publicly.
