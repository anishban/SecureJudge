from app.extensions import db
from app.models.job import Job
from app.services.queue_service import enqueue_job

def create_job(language, source_code):
    """
        Create a New Job in the database
    """
    job = Job(
        language = language,
        source_code = source_code,
        status = "queued"
    )

    db.session.add(job)
    db.session.commit()

    enqueue_job(job.id)

    return job

def get_job_by_id(job_id):
    return Job.query.get(job_id)

def list_jobs():
    return Job.query.order_by(Job.created_at.desc()).all()

def update_job(job_id, status):
    job = get_job_by_id(job_id)
    if job is None:
        return None
    
    job.status = status
    db.session.commit()
    return job

def save_job_result(job_id, stdout=None, stderr=None, exit_code=None, status="completed"):
    job = get_job_by_id(job_id)
    if job is None:
        return None
    
    job.stdout = stdout
    job.stderr = stderr
    job.exit_code = exit_code
    job.status = status

    db.session.commit()
    return job

