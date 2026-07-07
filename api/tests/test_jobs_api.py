from unittest.mock import patch


def test_submit_job_rejects_missing_json(client):
    response = client.post("/jobs")

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "request body must be valid json"


def test_submit_job_rejects_missing_language(client):
    response = client.post(
        "/jobs",
        json={
            "source_code": "print('hello')"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "language is required"


def test_submit_job_rejects_missing_source_code(client):
    response = client.post(
        "/jobs",
        json={
            "language": "python"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "source code is required"


def test_submit_job_rejects_unsupported_language(client):
    response = client.post(
        "/jobs",
        json={
            "language": "javascript",
            "source_code": "console.log('hello')"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Unsupported Language: javascript"


def test_submit_job_creates_queued_job(client):
    with patch("app.services.job_service.enqueue_job") as mock_enqueue_job:
        response = client.post(
            "/jobs",
            json={
                "language": "python",
                "source_code": "print('hello')"
            }
        )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == 1
    assert data["language"] == "python"
    assert data["source_code"] == "print('hello')"
    assert data["status"] == "queued"
    assert data["stdout"] is None
    assert data["stderr"] is None
    assert data["exit_code"] is None

    mock_enqueue_job.assert_called_once_with(1)


def test_get_existing_job(client):
    with patch("app.services.job_service.enqueue_job"):
        create_response = client.post(
            "/jobs",
            json={
                "language": "python",
                "source_code": "print('hello')"
            }
        )

    created_job = create_response.get_json()
    job_id = created_job["id"]

    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == job_id
    assert data["language"] == "python"
    assert data["source_code"] == "print('hello')"
    assert data["status"] == "queued"


def test_get_missing_job_returns_404(client):
    response = client.get("/jobs/999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "job not found"