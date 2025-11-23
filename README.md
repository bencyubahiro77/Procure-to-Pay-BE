# Procure-to-Pay — Starter App

## Quick start

1. Copy `.env.example` to `.env` and edit values if needed.

2. Build and run with Docker Compose:

```bash
docker-compose up --build
```

3. Run migrations and create superuser (the entrypoint creates superuser if env vars provided):

```bash
# inside container or use docker-compose exec
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

4. Access API docs: http://localhost:8000/api/docs/

## Endpoints (high-level)

- `POST /api/requests/` Create PR (staff)
- `GET /api/requests/` List PRs (staff see their own)
- `GET /api/requests/{id}/` PR details
- `PATCH /api/requests/{id}/approve/` Approve (approver)
- `PATCH /api/requests/{id}/reject/` Reject (approver)
- `POST /api/requests/{id}/submit-receipt/` Submit receipt (staff)

## Notes

- OCR and PDF parsing are basic placeholders; use LLM + better heuristics for production.
- Add tests and CI before public deployment.

# Seed default user

python manage.py seed_users
