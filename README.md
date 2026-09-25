# ChemsTools Project

This repository contains the source code for the ChemsTools application, an integrated platform for chemistry students and professionals.

## Project Structure

- **/frontend**: Next.js application (React)
- **/backend**: Django application (Python)
- **/docker**: Docker configurations (nginx)
- **/monitoring**: Prometheus, Grafana and Alertmanager configuration

## Quick Start

1.  Ensure you have Docker and Docker Compose installed.
2.  Copy `.env.example` to `.env` and set at least `SECRET_KEY`, `POSTGRES_PASSWORD` (also inside `DATABASE_URL`) and, if you use monitoring, `GRAFANA_ADMIN_PASSWORD`.
3.  Run `docker-compose up --build` from the root directory.
4.  Apply migrations: `docker-compose exec backend python manage.py migrate`.
5.  Optionally load sample data for the games and tools:
    `populate_quiz_questions`, `populate_chemwordle_words`, `populate_ph_examples` and `populate_substances`
    (`docker-compose exec backend python manage.py <command>`).
6.  Access the application:
    -   Frontend: [http://localhost:3000](http://localhost:3000)
    -   Backend API: [http://localhost:8000](http://localhost:8000) (docs at `/api/schema/swagger-ui/`)

## Running the backend without Docker

Copy `.env.example` to `backend/.env`, change the `db` and `redis` hosts to `localhost`, and run `python manage.py runserver` from `backend/`.
Without `SECRET_KEY` the server only starts when `DEBUG=True`.

## Tests

- Backend: `cd backend && pytest` (uses `chems_tools.settings_test`: in-memory SQLite and local cache; set `TEST_DATABASE_URL` to run against PostgreSQL).
- Frontend: `cd frontend && npm run lint && npm test && npm run build`.

CI (`.github/workflows/ci.yml`) runs both on pushes to `main`, `develop` and `v*` branches and on pull requests.
