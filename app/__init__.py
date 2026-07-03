from flask import Flask
from app.config import Config
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.models import Job

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Database initialized.")

    from app.routes.health import health_bp
    app.register_blueprint(health_bp)

    return app
    