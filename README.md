# SecureJudge

SecureJudge is a distributed code execution platform with a low-level React console frontend and a Flask API. It accepts Python submissions, stores jobs in PostgreSQL, queues execution work with Redis/RQ, and runs submitted code inside isolated Docker containers with resource limits.

This project is designed as a resume-ready backend/security project showing API design, asynchronous job processing, database persistence, containerized execution, and sandboxing fundamentals.

---

## Features

- Submit Python code through a React/Tailwind editor UI or REST API
- Poll job status from the frontend at 3-second intervals
- Store submitted jobs and execution results in PostgreSQL
- Process jobs asynchronously using Redis Queue
- Execute code inside Docker sandbox containers
- Disable network access inside execution containers
- Enforce CPU, memory, and timeout limits
- Capture stdout, stderr, exit code, and execution time
- Truncate excessive output
- Run the full local stack with Docker Compose
- Run locally on macOS, Windows, or Linux
- Reinitialize or fully reset the database during development
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
- React
- JavaScript
- Tailwind CSS
- Vite

---

## Architecture

```text
React Frontend
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
  api/
    app/
      models/
      routes/
      services/
    worker/
    tests/
    Dockerfile
    requirements.txt
  frontend/
    src/
      components/
      hooks/
      services/
    Dockerfile
    nginx.conf
    package.json
    tailwind.config.js
  .gitignore
  docker-compose.yml
  pytest.ini
  README.md
```

---

## Local Development with Docker

SecureJudge can be run locally using Docker Compose on macOS, Windows, or Linux.

Docker Compose starts the full local stack:

- PostgreSQL
- Redis
- Flask API
- RQ worker
- React frontend served by nginx

The frontend runs on host port `3000` and proxies `/api/*` to the Flask API. The API is also mapped directly to host port `5001`.

```text
http://127.0.0.1:3000
http://127.0.0.1:5001
```

Port `5001` is used for the API to avoid common conflicts with macOS services that use port `5000`.

---

## Prerequisites

### macOS

Install Docker Desktop:

```text
https://www.docker.com/products/docker-desktop/
```

Start Docker Desktop before running the project.

Verify Docker is working:

```bash
docker --version
docker compose version
```

---

### Windows

Install Docker Desktop for Windows:

```text
https://www.docker.com/products/docker-desktop/
```

During installation, enable WSL 2 support if prompted.

Recommended setup:

- Windows 10/11
- WSL 2 enabled
- Docker Desktop running
- Project opened from PowerShell, Windows Terminal, Git Bash, or WSL

Verify Docker is working from PowerShell:

```powershell
docker --version
docker compose version
```

If using WSL, verify Docker from the WSL terminal:

```bash
docker --version
docker compose version
```

---

### Linux

Install Docker Engine and the Docker Compose plugin.

For Ubuntu/Debian-based systems:

```bash
sudo apt update
sudo apt install docker.io docker-compose-plugin
```

Start Docker:

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

Verify Docker is working:

```bash
docker --version
docker compose version
```

If Docker commands require `sudo`, either run Docker commands with `sudo` or add your user to the Docker group:

```bash
sudo usermod -aG docker $USER
```

Then log out and log back in.

---

## Clone the Repository

```bash
git clone <your-repo-url>
cd SecureJudge
```

---

## Run the Project with Docker Compose

From the project root:

```bash
docker compose up --build
```

This builds the API/worker image and starts:

```text
securejudge-postgres
securejudge-redis
securejudge-api
securejudge-worker
```

Leave this terminal running.

The API should now be available at:

```text
http://127.0.0.1:5001
```

---

## Initialize the Database

Open a second terminal in the project root.

Run:

```bash
docker compose exec api python -m flask init-db
```

Expected output:

```text
Database initialized.
```

This command creates the database tables inside the PostgreSQL container.

---

## Test the Running App

Health check:

```bash
curl http://127.0.0.1:5001/health
```

Expected response:

```json
{
  "message": "SecureJudge is running",
  "status": "ok"
}
```

Submit a job:

```bash
curl -X POST http://127.0.0.1:5001/jobs \
  -H "Content-Type: application/json" \
  -d '{"language":"python","source_code":"print(\"hello from SecureJudge\")"}'
```

Example initial response:

```json
{
  "created_at": "2026-07-06T15:14:51.293810",
  "execution_time_ms": null,
  "exit_code": null,
  "finished_at": null,
  "id": 1,
  "language": "python",
  "source_code": "print(\"hello from SecureJudge\")",
  "started_at": null,
  "status": "queued",
  "stderr": null,
  "stdout": null
}
```

Fetch the job using the returned `id`:

```bash
curl http://127.0.0.1:5001/jobs/1
```

Expected final status:

```text
completed
```

Expected stdout:

```text
hello from SecureJudge
```

---

## Reinitialize the Database

Use this when you want to reset the database schema or delete existing job data.

### Option 1: Recreate Tables Only

This drops and recreates the tables while keeping the PostgreSQL Docker volume.

```bash
docker compose exec api python -m flask init-db
```

This is usually enough during development.

This deletes existing rows from the application tables, including previous job submissions.

---

### Option 2: Fully Reset Docker Volumes

This removes containers and deletes the PostgreSQL data volume.

```bash
docker compose down -v
docker compose up --build
```

Then initialize the database again:

```bash
docker compose exec api python -m flask init-db
```

Use this when the database volume itself may be stale, broken, or out of sync with the current schema.

---

### Option 3: Clear Redis Queue Only

If old queued jobs are still being processed, clear Redis:

```bash
docker compose exec redis redis-cli FLUSHALL
```

This clears queued/background job data from Redis without deleting PostgreSQL data.

---

## Stop the Project

Stop containers while keeping database data:

```bash
docker compose down
```

Stop containers and delete database data:

```bash
docker compose down -v
```

---

## Run in Background

Start services in detached mode:

```bash
docker compose up --build -d
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

Stop background services:

```bash
docker compose down
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

## Example Execution Cases

### Successful Python Execution

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

### Runtime Error

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

### Large Output Truncation

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

### Network Disabled

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

Install dependencies first if running tests outside Docker:

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

The API tests mock queue submission so tests do not require Redis, Docker, PostgreSQL, or the worker.

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

Initialize or reinitialize database tables:

```bash
docker compose exec api python -m flask init-db
```

Fully reset the database volume:

```bash
docker compose down -v
docker compose up --build
docker compose exec api python -m flask init-db
```

Clear Redis:

```bash
docker compose exec redis redis-cli FLUSHALL
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

Exit PostgreSQL shell:

```sql
\q
```

---

## Platform Notes

### macOS

If port `5000` is already in use, it may be caused by AirPlay Receiver. SecureJudge maps the API to host port `5001` to avoid this issue.

Use:

```bash
curl http://127.0.0.1:5001/health
```

not:

```bash
curl http://127.0.0.1:5000/health
```

---

### Windows

Recommended terminals:

- PowerShell
- Windows Terminal
- Git Bash
- WSL terminal

If using PowerShell, the `curl` command may behave differently because PowerShell aliases `curl` to `Invoke-WebRequest`.

Use `curl.exe` if needed:

```powershell
curl.exe http://127.0.0.1:5001/health
```

For POST requests in PowerShell, use backticks for line continuation:

```powershell
curl.exe -X POST http://127.0.0.1:5001/jobs `
  -H "Content-Type: application/json" `
  -d "{\"language\":\"python\",\"source_code\":\"print(\\\"hello from SecureJudge\\\")\"}"
```

Using WSL or Git Bash is usually simpler for the Unix-style curl commands shown elsewhere in this README.

---

### Linux

If Docker requires root permissions, use:

```bash
sudo docker compose up --build
```

or add your user to the Docker group:

```bash
sudo usermod -aG docker $USER
```

Then log out and log back in.

---

## Troubleshooting

### API does not start because port is already in use

Check what is using port `5001`.

On macOS/Linux:

```bash
lsof -i :5001
```

Then either stop that process or change the host port in `docker-compose.yml`.

Current mapping:

```yaml
ports:
  - "5001:5000"
```

Change `5001` to another available host port if needed.

---

### Worker cannot execute jobs

Check worker logs:

```bash
docker compose logs -f worker
```

The worker needs access to the Docker socket:

```yaml
- /var/run/docker.sock:/var/run/docker.sock
```

This is required for the local development setup because the worker starts sandbox containers for code execution.

---

### Sandbox container cannot find `main.py`

If job stderr contains something like:

```text
python: can't open file '/sandbox/main.py': [Errno 2] No such file or directory
```

make sure the Compose worker service has sandbox environment variables similar to:

```yaml
SANDBOX_HOST_DIR: ${PWD}/.sandbox_runs
SANDBOX_CONTAINER_DIR: /app/.sandbox_runs
```

and that `.sandbox_runs/` exists or can be created by the worker.

---

### Database connection errors

Make sure PostgreSQL is running:

```bash
docker compose ps
```

Reinitialize the database:

```bash
docker compose exec api python -m flask init-db
```

If problems continue, fully reset volumes:

```bash
docker compose down -v
docker compose up --build
docker compose exec api python -m flask init-db
```

---

### Old Redis jobs are still being processed

Clear Redis:

```bash
docker compose exec redis redis-cli FLUSHALL
```

---

### Python package changes are not reflected inside Docker

Rebuild the Docker image without cache:

```bash
docker compose down
docker compose build --no-cache
docker compose up
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
- There is no Kubernetes, Firecracker, or gVisor-based isolation layer yet.

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
