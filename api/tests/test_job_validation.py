from app.constants import MAX_SOURCE_CODE_LENGTH
from app.services.job_validation_services import validate_job_submission


def test_validation_rejects_missing_json():
    is_valid, error = validate_job_submission(None)

    assert is_valid is False
    assert error == "request body must be valid json"


def test_validation_rejects_missing_language():
    data = {
        "source_code": "print('Hello, World!')"
    }

    is_valid, error = validate_job_submission(data)

    assert is_valid is False
    assert error == "language is required"


def test_validation_rejects_missing_source_code():
    data = {
        "language": "python"
    }

    is_valid, error = validate_job_submission(data)

    assert is_valid is False
    assert error == "source code is required"


def test_validation_rejects_non_string_language():
    data = {
        "language": 123,
        "source_code": "print('Hello, World!')"
    }

    is_valid, error = validate_job_submission(data)

    assert is_valid is False
    assert error == "language must be a string"


def test_validation_rejects_non_string_source_code():
    data = {
        "language": "python",
        "source_code": 123
    }

    is_valid, error = validate_job_submission(data)

    assert is_valid is False
    assert error == "source code must be a string"


def test_validation_rejects_empty_language():
    data = {
        "language": "",
        "source_code": "print('Hello, World!')"
    }

    is_valid, error = validate_job_submission(data)

    assert is_valid is False
    assert error == "language cannot be empty"


def test_validation_rejects_empty_source_code():
    data = {
        "language": "python",
        "source_code": ""
    }

    is_valid, error = validate_job_submission(data)

    assert is_valid is False
    assert error == "source code cannot be empty"


def test_validation_rejects_unsupported_language():
    data = {
        "language": "javascript",
        "source_code": "console.log('hello')"
    }

    is_valid, error = validate_job_submission(data)

    assert is_valid is False
    assert error == "Unsupported Language: javascript"


def test_validation_rejects_too_large_source_code():
    data = {
        "language": "python",
        "source_code": "x" * (MAX_SOURCE_CODE_LENGTH + 1)
    }

    is_valid, error = validate_job_submission(data)

    assert is_valid is False
    assert error == f"Source code cannot exceed {MAX_SOURCE_CODE_LENGTH} characters"


def test_validation_accepts_valid_python_job():
    data = {
        "language": "python",
        "source_code": "print('hello')"
    }

    is_valid, error = validate_job_submission(data)

    assert is_valid is True
    assert error is None