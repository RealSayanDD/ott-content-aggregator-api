# Catalog, Discovery and Watchlist API

This module adds database-backed catalog discovery to the existing FastAPI application. It does **not** fetch data from Netflix, Prime Video, or another external service. An administrator creates local `Title`, `Genre`, and `Platform` records, and the API exposes those records for discovery.

## Data model

- `Title`: name, synopsis, movie/series type, optional release year, maturity rating, runtime, publication state, genres, and platforms.
- `Genre` and `Platform`: named, slug-addressable catalog metadata.
- `WatchlistEntry`: one row per user/title with a private `is_favorite` flag.

Titles have many-to-many relationships with genres and platforms. Deleting a genre or platform removes that relationship; it does not delete the title. Watchlist rows are deleted with their user or title through database foreign keys (production databases should enforce foreign keys).

## Public discovery

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness response |
| GET | `/ready` | Database readiness; reports Redis as `ok` or optional `disabled` |
| GET | `/api/titles` | Published titles with filtering, sorting, and pagination |
| GET | `/api/titles/{id}` | One published title |
| GET | `/api/genres` | Genre discovery |
| GET | `/api/genres/{slug}` | One genre |
| GET | `/api/platforms` | Active platform discovery |
| GET | `/api/platforms/{slug}` | One active platform |

`GET /api/titles` supports `offset` (default `0`), `limit` (default `20`, max `100`), `q`, `content_type` (`movie` or `series`), `genre`, `platform`, `release_year`, `sort_by` (`name`, `release_year`, `created_at`), and `sort_order` (`asc`, `desc`). Public title routes intentionally exclude unpublished records.

Example:

```http
GET /api/titles?q=orbit&genre=science-fiction&platform=example-stream&sort_by=name&sort_order=asc
```

```json
{
  "data": [{"id": 12, "name": "Orbit", "content_type": "movie", "genres": [{"slug": "science-fiction"}], "platforms": [{"slug": "example-stream"}]}],
  "meta": {"offset": 0, "limit": 20, "total": 1}
}
```

## Administrator catalog writes

All catalog writes require an existing JWT with the `admin` role.

| Method | Path |
|---|---|
| POST, PATCH, DELETE | `/api/titles`, `/api/titles/{id}` |
| POST, PATCH, DELETE | `/api/genres`, `/api/genres/{slug}` |
| POST, PATCH, DELETE | `/api/platforms`, `/api/platforms/{slug}` |

Example title request:

```json
{
  "name": "Orbit",
  "content_type": "movie",
  "release_year": 2025,
  "synopsis": "A science-fiction drama.",
  "genre_ids": [1],
  "platform_ids": [2],
  "is_published": true
}
```

Unknown related IDs return `422`; duplicate genre/platform names or slugs return `409`. Schemas constrain string lengths, valid URLs, title types, years, pagination, and sort fields.

## Private watchlist and favorites

These routes require any authenticated user and only return that user’s own records.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/users/me/watchlist` | Paginated watchlist |
| PUT | `/api/users/me/watchlist/{title_id}` | Add a published title (idempotent) |
| PATCH | `/api/users/me/watchlist/{title_id}` | Set `is_favorite` |
| DELETE | `/api/users/me/watchlist/{title_id}` | Remove it |
| GET | `/api/users/me/favorites` | Paginated favorite entries |

```http
PATCH /api/users/me/watchlist/12
Authorization: Bearer <access-token>
Content-Type: application/json

{"is_favorite": true}
```

## Provider availability

Netflix, Prime Video, and JioHotstar are represented by ordinary `Platform` records. The API deliberately does not scrape their private services or impersonate provider APIs. An admin can add verified regional availability data from an approved provider feed or a licensed data source.

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/api/titles/{title_id}/availability` | public | Current availability, optionally filtered by `country=IN` |
| POST | `/api/titles/{title_id}/availability` | admin | Add a title/platform/country availability record |
| DELETE | `/api/titles/{title_id}/availability/{availability_id}` | admin | Remove an availability record |

```json
{
  "platform_id": 1,
  "country_code": "IN",
  "provider_content_id": "provider-owned-id",
  "url": "https://provider.example/title",
  "available_from": null,
  "available_until": null
}
```

To automate ingestion later, obtain a documented, licensed provider feed and add an integration adapter; do not use private application endpoints, user cookies, or scraping.

<<<<<<< HEAD
## Background provider sync

`POST /api/admin/provider-sync` accepts an administrator JWT and queues a safe,
deterministic mock provider sync. The task opens its own database session and
creates or updates a sample title, platform, genre, and regional availability
record without calling an external website. It demonstrates the asynchronous
ingestion architecture required for the project; replace `MockProviderClient`
with a licensed, documented provider-feed adapter before production use.

=======
>>>>>>> 1bcbadd82c111adbbcf28b5f690d1e797f587b42
## Redis behavior

The existing Redis helper remains optional: cache failures do not stop reads. Published title list and detail responses are cached under the `catalog:` namespace using the configured `REDIS_DEFAULT_TTL`. Title writes invalidate title-list keys and the changed detail key. Genre or platform writes invalidate both title-list and title-detail keys because those objects are embedded in title responses. Invalidation uses Redis `SCAN`, not blocking `KEYS`.

## Run and test

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload
pytest -q
```

SQLite is the default development database. `init_db()` creates tables for local development. The repository has no Alembic configuration or migrations yet, so create and apply a migration before using these new tables in an existing production database.
