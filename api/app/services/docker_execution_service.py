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
    if output is None:
        return ""

    if isinstance(output, bytes):
        output = output.decode("utf-8", errors="replace")

    if len(output) <= max_length:
        return output

    return output[:max_length] + "\n...[output truncated]"


def execute_python_code_in_docker(
    source_code,
    timeout_seconds=DEFAULT_EXECUTION_TIMEOUT_SECONDS
):
    container_name = f"securejudge-{uuid.uuid4().hex}"
    start_time = time.perf_counter()

    sandbox_container_base_dir = os.getenv(
        "SANDBOX_CONTAINER_DIR",
        tempfile.gettempdir()
    )

    sandbox_host_base_dir = os.getenv(
        "SANDBOX_HOST_DIR",
        sandbox_container_base_dir
    )

    temp_dir = None

    try:
        os.makedirs(sandbox_container_base_dir, exist_ok=True)

        temp_dir = tempfile.mkdtemp(dir=sandbox_container_base_dir)

        temp_dir_name = os.path.basename(temp_dir)
        host_temp_dir = os.path.join(sandbox_host_base_dir, temp_dir_name)

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
            "-v", f"{host_temp_dir}:/sandbox:ro",
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
            "stdout": _truncate_output(completed_process.stdout, MAX_STDOUT_LENGTH),
            "stderr": _truncate_output(completed_process.stderr, MAX_STDERR_LENGTH),
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

        return {
            "stdout": _truncate_output(error.stdout or "", MAX_STDOUT_LENGTH),
            "stderr": _truncate_output(error.stderr or "Execution timed out.", MAX_STDERR_LENGTH),
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
