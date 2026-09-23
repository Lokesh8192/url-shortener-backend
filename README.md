# URL Shortener API

A FastAPI service for creating short links, redirecting visitors, and viewing
per-link click analytics. URLs are private to their owner; only the public
redirect endpoint is unauthenticated.

## Run locally

1. Copy `.env.example` to `.env` and set the database connection strings and a
   strong `SECRET_KEY`.
2. Create the database schema with `alembic upgrade head`.
3. Start the API with `uvicorn app.main:app --reload`.

Interactive documentation is available at `/docs`.

## API endpoints

| Method | Endpoint | Authentication | Purpose |
| --- | --- | --- | --- |
| POST | `/auth/register` | No | Create an account |
| POST | `/auth/login` | No | Receive a bearer access token |
| GET | `/users/me` | Bearer token | View the current user |
| POST | `/urls` | Bearer token | Create a short URL |
| GET | `/urls` | Bearer token | List the current user's URLs |
| GET | `/urls/{url_id}` | Bearer token | Get one URL |
| PATCH | `/urls/{url_id}` | Bearer token | Update destination, expiry, or active state |
| DELETE | `/urls/{url_id}` | Bearer token | Delete one URL |
| GET | `/urls/{url_id}/stats` | Bearer token | Get click statistics |
| GET | `/{short_code}` | No | Redirect to the destination URL |
| GET | `/health` | No | Health check |

For protected routes, send `Authorization: Bearer <access_token>`. A `PATCH`
body must contain at least one of `original_url`, `expires_at`, or `is_active`.
Set `expires_at` to `null` to remove an existing expiration.
