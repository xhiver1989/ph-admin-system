# ph-admin-system

## Setup

### Local run (venv)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Docker Compose

```bash
docker-compose up
```

## Authentication

Seeded admin user:

- Email: `admin@local.test`
- Password: `Admin123!`
- Role: `ADMIN`

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@local.test","password":"Admin123!"}'
```

### Refresh

```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
```

### Get profile

```bash
curl http://localhost:8000/me \
  -H "Authorization: Bearer <access_token>"
```

### Health

```bash
curl http://localhost:8000/health
```

## Role protection

Use the `require_roles("ADMIN")` dependency to protect endpoints.
