from flask import Flask
from app.config import Config
from app.extensions import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from app.models import Job

    @app.cli.command("init-db")
    def init_db():
        db.drop_all()
        db.create_all()
        print("Database initialized.")

    from app.routes.health import health_bp
    app.register_blueprint(health_bp)

    from app.routes.jobs import jobs_bp
    app.register_blueprint(jobs_bp)

    return app
    