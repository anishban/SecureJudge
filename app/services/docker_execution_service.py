import os
import shutil
import subprocess
import tempfile
import time
import uuid

from app.constants import (
    DEFAULT_EXECUTION_TIMEOUT_SECONDS,
    DOCKER_CPU_LIMIT,
    DOCKER_MEMORY_LIMIT,
    MAX_STDERR_LENGTH,
    MAX_STDOUT_LENGTH,
    PYTHON_DOCKER_IMAGE,
)


def _truncate_output(output, max_length):
    """
    Prevent extremely large stdout/stderr from being stored in the database.
    """

    if output is None:
        return ""

    if len(output) <= max_length:
        return output

    return output[:max_length] + "\n...[output truncated]"


def execute_python_code_in_docker(
    source_code,
    timeout_seconds=DEFAULT_EXECUTION_TIMEOUT_SECONDS
):
    """
    Execute Python source code inside a temporary Docker container.

    Safeguards:
    - unique container name
    - network disabled
    - memory limit
    - CPU limit
    - timeout
    - forced container cleanup on timeout
    - temp directory cleanup
    - stdout/stderr truncation
    - Docker unavailable handling
    """

    temp_dir = None
    container_name = f"securejudge-{uuid.uuid4().hex}"
    start_time = time.perf_counter()

    try:
        temp_dir = tempfile.mkdtemp()
        code_file_path = os.path.join(temp_dir, "main.py")

        with open(code_file_path, "w", encoding="utf-8") as code_file:
            code_file.write(source_code)

        docker_command = [
            "docker",
            "run",
            "--name", container_name,
            "--rm",
            "--network", "none",
            "--memory", DOCKER_MEMORY_LIMIT,
            "--cpus", DOCKER_CPU_LIMIT,
            "-v", f"{temp_dir}:/sandbox:ro",
            "-w", "/sandbox",
            PYTHON_DOCKER_IMAGE,
            "python",
            "main.py",
        ]

        completed_process = subprocess.run(
            docker_command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        execution_time_ms = int((time.perf_counter() - start_time) * 1000)

        return {
            "stdout": _truncate_output(
                completed_process.stdout,
                MAX_STDOUT_LENGTH
            ),
            "stderr": _truncate_output(
                completed_process.stderr,
                MAX_STDERR_LENGTH
            ),
            "exit_code": completed_process.returncode,
            "timed_out": False,
            "execution_time_ms": execution_time_ms,
            "internal_error": False,
        }

    except subprocess.TimeoutExpired as error:
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            capture_output=True,
            text=True,
        )

        execution_time_ms = int((time.perf_counter() - start_time) * 1000)

        stdout = error.stdout or ""
        stderr = error.stderr or "Execution timed out."

        return {
            "stdout": _truncate_output(stdout, MAX_STDOUT_LENGTH),
            "stderr": _truncate_output(stderr, MAX_STDERR_LENGTH),
            "exit_code": None,
            "timed_out": True,
            "execution_time_ms": execution_time_ms,
            "internal_error": False,
        }

    except FileNotFoundError:
        execution_time_ms = int((time.perf_counter() - start_time) * 1000)

        return {
            "stdout": "",
            "stderr": "Docker is not installed or not available in PATH.",
            "exit_code": None,
            "timed_out": False,
            "execution_time_ms": execution_time_ms,
            "internal_error": True,
        }

    except Exception as error:
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            capture_output=True,
            text=True,
        )

        execution_time_ms = int((time.perf_counter() - start_time) * 1000)

        return {
            "stdout": "",
            "stderr": f"Internal execution error: {str(error)}",
            "exit_code": None,
            "timed_out": False,
            "execution_time_ms": execution_time_ms,
            "internal_error": True,
        }

    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)