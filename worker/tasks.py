import time
from datetime import datetime, timezone

from app import create_app
from app.extensions import db
from app.services.job_service import get_job_by_id

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

        time.sleep(2)

        job.status = "completed"
        job.stdout = "Fake execution completed"
        job.stderr = None
        job.exit_code = 0
        job.finished_at = datetime.now(timezone.utc)

        db.session.commit()

        print(f"Job {job_id} completed.")