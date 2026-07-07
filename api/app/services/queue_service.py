import redis
from flask import current_app
from rq import Queue

def get_redis_connection():
    redis_url = current_app.config["REDIS_URL"]
    return redis.from_url(redis_url)

def get_job_queue():
    redis_connection = get_redis_connection()
    return Queue("jobs",connection=redis_connection)

def enqueue_job(job_id):
    queue = get_job_queue()

    queued_job = queue.enqueue(
        "worker.tasks.process_job",
        job_id
    )
    return queued_job
