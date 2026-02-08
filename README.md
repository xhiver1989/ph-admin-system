# PH Admin System

## Descripción
Monorepo para el sistema administrativo de propiedad horizontal (core + web + placeholders de visión).

## Estructura
```
/apps/api-core
/apps/web
/apps/vision-face
/apps/vision-anpr
/infra/docker-compose.yml
```

## Requisitos
- Docker + Docker Compose

## Arranque local
```bash
docker compose -f infra/docker-compose.yml up --build
```

Servicios:
- API Core: http://localhost:8000/docs
- Healthcheck: http://localhost:8000/health
- Web: http://localhost:5173

## Seed inicial
El API crea un usuario administrador en el arranque:
- Email: `admin@local.test`
- Password: `Admin123!`

Roles semilla: `ADMIN`, `MANAGER`, `ACCOUNTANT`, `GUARD`.
Permisos base: `USER:MANAGE`, `BUILDING:READ`, `BUILDING:WRITE`.

## Uso de autenticación
### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@local.test","password":"Admin123!"}'
```

### Crear usuario (solo ADMIN)
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@local.test","password":"Password123!","full_name":"User"}'
```

### Asignar roles (temporal)
Mientras no exista endpoint de administración de roles, se puede asignar en la BD:
```sql
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u, roles r
WHERE u.email = 'user@local.test' AND r.name = 'MANAGER';
```
