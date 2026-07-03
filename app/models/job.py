from datetime import datetime, timezone

from app.extensions import db

class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)

    language = db.Column(db.String(50), nullable=False)
    source_code = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(50), nullable=False, default="queued")

    stdout = db.Column(db.Text, nullable=True)
    stderr = db.Column(db.Text, nullable=True)
    exit_code = db.Column(db.Integer, nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return{
            "id":self.id,
            "language":self.language,
            "source_code":self.source_code,
            "status":self.status,
            "stdout":self.stdout,
            "stderr":self.stderr,
            "exit_code":self.exit_code,
            "created_at":self.created_at.isoformat() if self.created_at else None,
            "started_at":self.started_at.isoformat() if self.started_at else None,
            "finished_at":self.finished_at.isoformat() if self.finished_at else None,
        }