# Authentication, Authorization & User Management

JWT authentication, role-based authorization (`user` / `admin`) and user management.
Async throughout (FastAPI, SQLAlchemy 2.x async, Pydantic v2).

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # then set a strong SECRET_KEY
uvicorn src.main:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs (use the **Authorize** button to log in).

## Tests

```bash
pytest
```

20 tests covering registration, login, refresh tokens, token misuse, role checks and admin actions.
They use an in-memory SQLite database, so no setup is needed.

## Endpoints

| Method | Path | Access | Purpose |
|---|---|---|---|
| POST | `/api/auth/register` | public | Create account (always role `user`) |
| POST | `/api/auth/login` | public | Login with username **or** email, returns access + refresh token |
| POST | `/api/auth/refresh` | public | Exchange a refresh token for a new token pair |
| GET | `/api/users/me` | logged in | Own profile |
| PATCH | `/api/users/me` | logged in | Update own email / username / full name |
| POST | `/api/users/me/change-password` | logged in | Change own password |
| GET | `/api/users` | admin | List users (`skip`, `limit`) |
| GET | `/api/users/{id}` | admin | Get one user |
| PATCH | `/api/users/{id}` | admin | Change role, activate / deactivate, edit |
| DELETE | `/api/users/{id}` | admin | Delete a user |

## Protecting other routes (titles, genres, platforms)

```python
from fastapi import Depends
from src.api.deps import get_current_user, require_admin
from src.models.user import User

@router.get("")                                   # any logged-in user
async def list_titles(user: User = Depends(get_current_user)): ...

@router.post("")                                  # admin only
async def add_title(admin: User = Depends(require_admin)): ...
```

## Files

```
src/core/config.py       settings (SECRET_KEY, token lifetimes, DATABASE_URL added)
src/core/security.py     bcrypt password hashing, JWT create / decode
src/db/base.py           shared SQLAlchemy Base, every model should inherit this
src/db/session.py        async engine, get_db dependency, init_db
src/models/user.py       User model, UserRole enum
src/schemas/             user.py, token.py (Pydantic models)
src/services/            user_service.py (all user DB logic)
src/api/deps.py          get_current_user, require_roles, require_admin
src/api/auth.py          register / login / refresh
src/api/users.py         profile + admin user management
tests/                   pytest suite
```

## Notes for the team

- **Shared Base:** Title, Genre and Platform models should inherit `Base` from `src/db/base.py`,
  and be imported inside `init_db()` in `src/db/session.py` (next to the `user` import) so their
  tables are created too. For Alembic, set `target_metadata = Base.metadata`.
- **Database:** defaults to SQLite so it runs anywhere. For PostgreSQL set
  `DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ott` in `.env`.
- **Passwords:** bcrypt, 8-72 characters, at least one letter and one digit.
- **Tokens:** access token 30 min, refresh token 7 days (configurable). A `type` claim stops a
  refresh token being used as an access token.
- **Deactivated users** are blocked at login and on every request, even with an old token.
- **Admins** cannot demote, deactivate or delete themselves. Public signup only creates normal
  users, so the first admin must be created directly in the database.
- **requirements.txt:** `greenlet` was added because SQLAlchemy async needs it and it was missing.
- Never commit `.env`. The included `.gitignore` excludes it, along with `__pycache__` and `*.db`.
