# SecureJudge

SecureJudge is a backend-focused distributed code execution platform. It accepts code submissions through a Flask API, stores jobs in PostgreSQL, queues execution work with Redis/RQ, and runs submitted Python code inside isolated Docker containers with resource limits.

This project is designed as a resume-ready backend/security project showing API design, asynchronous job processing, database persistence, containerized execution, and sandboxing fundamentals.

---

## Features

- Submit Python code through a REST API
- Store submitted jobs and execution results in PostgreSQL
- Process jobs asynchronously using Redis Queue
- Execute code inside Docker sandbox containers
- Disable network access inside execution containers
- Enforce CPU, memory, and timeout limits
- Capture stdout, stderr, exit code, and execution time
- Truncate excessive output
- Run full local stack with Docker Compose
- Automated tests for API and validation logic

---

## Tech Stack

- Python 3.12
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- Redis
- RQ
- Docker
- Docker Compose
- pytest

---

## Architecture

```text
Client
  |
  | HTTP request
  v
Flask API
  |
  | creates job
  v
PostgreSQL
  |
  | enqueues job id
  v
Redis Queue
  |
  | worker consumes job
  v
RQ Worker
  |
  | runs submitted code
  v
Docker Sandbox Container
  |
  | stdout/stderr/exit code/time
  v
PostgreSQL
```

---

## Project Structure

```text
SecureJudge/
  app/
    __init__.py
    config.py
    constants.py
    extensions.py
    models/
      job.py
    routes/
      health.py
      jobs.py
    services/
      docker_execution_service.py
      job_service.py
      job_validation_service.py
      queue_service.py
  worker/
    worker.py
    tasks.py
  tests/
    conftest.py
    test_health.py
    test_job_validation.py
    test_jobs_api.py
  docker-compose.yml
  Dockerfile
  requirements.txt
  README.md
```

---

## Local Development Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd SecureJudge
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Running with Docker Compose

Docker Compose starts:

- PostgreSQL
- Redis
- Flask API
- RQ worker

From the project root:

```bash
docker compose up --build
```

The API runs on:

```text
http://127.0.0.1:5001
```

The Flask app runs inside the container on port `5000`, but it is mapped to host port `5001` to avoid common macOS conflicts with port `5000`.

---

## Initialize the Database

In another terminal:

```bash
docker compose exec api python -m flask init-db
```

Expected output:

```text
Database initialized.
```

---

## API Endpoints

### Health Check

```http
GET /health
```

Example:

```bash
curl http://127.0.0.1:5001/health
```

Example response:

```json
{
  "message": "SecureJudge is running",
  "status": "ok"
}
```

---

### Submit Job

```http
POST /jobs
```

Request body:

```json
{
  "language": "python",
  "source_code": "print(\"hello\")"
}
```

Example:

```bash
curl -X POST http://127.0.0.1:5001/jobs \
  -H "Content-Type: application/json" \
  -d '{"language":"python","source_code":"print(\"hello from SecureJudge\")"}'
```

Example response:

```json
{
  "id": 1,
  "language": "python",
  "source_code": "print(\"hello from SecureJudge\")",
  "status": "queued",
  "stdout": null,
  "stderr": null,
  "exit_code": null,
  "created_at": "2026-07-06T15:14:51.293810",
  "started_at": null,
  "finished_at": null,
  "execution_time_ms": null
}
```

---

### Get Job

```http
GET /jobs/<job_id>
```

Example:

```bash
curl http://127.0.0.1:5001/jobs/1
```

Example completed response:

```json
{
  "id": 1,
  "language": "python",
  "source_code": "print(\"hello from SecureJudge\")",
  "status": "completed",
  "stdout": "hello from SecureJudge\n",
  "stderr": "",
  "exit_code": 0,
  "created_at": "2026-07-06T15:14:51.293810",
  "started_at": "2026-07-06T15:14:51.424805",
  "finished_at": "2026-07-06T15:14:52.221981",
  "execution_time_ms": 789
}
```

---

## Job Statuses

```text
queued      - Job has been accepted and added to the queue
running     - Worker is currently executing the job
completed   - Job finished successfully with exit code 0
failed      - Job failed due to runtime error or internal execution error
timed_out   - Job exceeded the execution timeout
```

---

## Example Test Cases

### Successful Python execution

```bash
curl -X POST http://127.0.0.1:5001/jobs \
  -H "Content-Type: application/json" \
  -d '{"language":"python","source_code":"print(\"hello\")"}'
```

Expected result after fetching the job:

```text
status: completed
stdout: hello
exit_code: 0
```

---

### Runtime error

```bash
curl -X POST http://127.0.0.1:5001/jobs \
  -H "Content-Type: application/json" \
  -d '{"language":"python","source_code":"print(undefined_variable)"}'
```

Expected result:

```text
status: failed
stderr contains NameError
exit_code: 1
```

---

### Timeout

```bash
curl -X POST http://127.0.0.1:5001/jobs \
  -H "Content-Type: application/json" \
  -d '{"language":"python","source_code":"while True:\n    pass"}'
```

Expected result:

```text
status: timed_out
exit_code: null
execution_time_ms around timeout duration
```

---

### Large output truncation

```bash
curl -X POST http://127.0.0.1:5001/jobs \
  -H "Content-Type: application/json" \
  -d '{"language":"python","source_code":"print(\"x\" * 50000)"}'
```

Expected result:

```text
stdout ends with ...[output truncated]
```

---

### Network disabled

```bash
curl -X POST http://127.0.0.1:5001/jobs \
  -H "Content-Type: application/json" \
  -d '{"language":"python","source_code":"import urllib.request\nurllib.request.urlopen(\"https://google.com\")"}'
```

Expected result:

```text
status: failed
stderr contains a network-related error
```

---

## Running Tests

Install dependencies first:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

Verbose mode:

```bash
pytest -v
```

The test suite currently covers:

- Health endpoint
- Job validation logic
- Job creation API
- Job retrieval API
- Invalid request handling
- 404 handling

The API tests mock queue submission so tests do not require Redis, Docker, or the worker.

---

## Useful Docker Compose Commands

Start the full stack:

```bash
docker compose up
```

Start and rebuild:

```bash
docker compose up --build
```

Run in background:

```bash
docker compose up -d
```

Stop containers:

```bash
docker compose down
```

Stop containers and delete database volume:

```bash
docker compose down -v
```

View logs:

```bash
docker compose logs api
docker compose logs worker
docker compose logs postgres
docker compose logs redis
```

Follow worker logs:

```bash
docker compose logs -f worker
```

Open PostgreSQL shell:

```bash
docker compose exec postgres psql -U securejudge -d securejudge_db
```

View recent jobs:

```sql
SELECT id, language, status, exit_code, execution_time_ms, created_at
FROM jobs
ORDER BY created_at DESC
LIMIT 10;
```

---

## Security Model

SecureJudge runs submitted code inside Docker containers with:

- No network access
- Read-only mounted source directory
- Memory limit
- CPU limit
- Execution timeout
- Temporary file cleanup
- Output truncation

The execution container is created per job and removed after execution.

---

## Security Limitations

This project is a learning and portfolio project. It should not be treated as production-grade untrusted code execution.

Current limitations:

- The Docker socket is mounted into the worker container for local development.
- Mounting `/var/run/docker.sock` gives the worker powerful access to the host Docker engine.
- Docker alone is not a complete security boundary for hostile code.
- There is no user authentication yet.
- There is no rate limiting yet.
- There is no per-user quota system yet.
- There is no advanced syscall filtering or seccomp profile yet.
- There is no Kubernetes/firecracker/gVisor-based isolation layer yet.

For production, this system would need stronger isolation, strict resource quotas, authentication, authorization, monitoring, and infrastructure-level sandbox hardening.

---

## Local macOS Note

For local macOS development, the worker uses RQ `SimpleWorker` instead of the default RQ `Worker`.

The default RQ worker forks child processes. On macOS, that can cause instability in some Python/Docker workflows. `SimpleWorker` runs jobs in the same process and is more reliable for local development.

In a Linux production-like environment, the standard RQ `Worker` can be considered.

---

## Future Improvements

Planned improvements:

- Add Flask-Migrate/Alembic for database migrations
- Add authentication with JWT
- Add user accounts
- Add per-user job history
- Add rate limiting
- Add support for more languages
- Add admin dashboard
- Add structured logging
- Add metrics and monitoring
- Add integration tests for Docker execution
- Add stronger sandboxing with seccomp, gVisor, or Firecracker
- Add CI pipeline with GitHub Actions

---

## Status

Current version includes:

- Flask REST API
- PostgreSQL persistence
- Redis/RQ asynchronous execution
- Docker-based Python sandbox
- Docker Compose local development setup
- pytest test suite

This is the first stable backend version of SecureJudge.