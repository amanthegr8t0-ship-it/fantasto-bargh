from celery import Celery
from controllers import podcast_controller  as pc
from core.config import REDIS_URL
import base64
from core.database import SessionLocal, Job
from datetime import datetime

celery_app = Celery(
    "podcast",
    broker=REDIS_URL,
    backend=REDIS_URL
)
def update_job_status(db, job_id, status, error_message=None):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if job:
        job.status = status
        job.error_message = error_message
        job.completed_at = datetime.now()

@celery_app.task(bind = True)
def generate_podcast_task(self, text, model):
    db = SessionLocal()
    try:
        output = pc.generate_pdf_to_podcast(text, model)
        encoded = base64.b64encode(output).decode("utf-8")
        update_job_status(db, self.request.id, "Completed")
        db.commit()
        return encoded
    except Exception as e:
        update_job_status(db, self.request.id, "Failed", str(e))
        db.commit()
        raise e
    

    finally:
        db.close()

@celery_app.task(bind = True)
def generate_text_to_speech_task(self, text, model):
    db = SessionLocal()
    try:
        output = pc.generate_text_to_speech(text, model)
        encoded = base64.b64encode(output).decode("utf-8")
        update_job_status(db, self.request.id, "Completed")
        db.commit()
        return encoded
    except Exception as e:
        update_job_status(db, self.request.id, "Failed", str(e))
        db.commit()
        raise e
    finally:
        db.close()