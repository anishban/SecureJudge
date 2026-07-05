import time
from datetime import datetime, timezone

from app import create_app
from app.extensions import db
from app.services.job_service import get_job_by_id
from app.services.docker_execution_service import execute_python_code_in_docker

def process_job(job_id):
    app = create_app()

    with app.app_context():
        job = get_job_by_id(job_id)

        if job is None:
            print(f"Job {job_id} not found")
            return
        
        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        db.session.commit()

        result = execute_python_code_in_docker(job.source_code)

        job.stdout = result['stdout']
        job.stderr = result['stderr']
        job.exit_code = result['exit_code']
        job.finished_at = datetime.now(timezone.utc)

        if result['timed_out']:
            job.status = "timed_out"
        elif result['exit_code'] == 0:
            job.status = "completed"
        else:
            job.status = "failed"

        db.session.commit()

        print(f"Job {job_id} finished with status {job.status}.")