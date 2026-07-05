import redis
from rq import SimpleWorker, Queue

from app import create_app

def start_worker():
    app = create_app()

    with app.app_context():
        redis_url = app.config["REDIS_URL"]
        redis_connection = redis.from_url(redis_url)

        queues = [
            Queue("jobs", connection=redis_connection)
        ]

        worker = SimpleWorker(queues, connection=redis_connection)
        worker.work()

if __name__ == "__main__":
    start_worker()
