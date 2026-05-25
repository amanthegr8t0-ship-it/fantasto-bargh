from celery import Celery
from controllers import podcast_controller  as pc
from core.config import REDIS_URL
import base64
from core.database import SessionLocal, Job
from datetime import datetime
import faiss
import json
from Services.retrieval import store_embedded
from core.redis_client import redis_client
from utils.chunking import chunk_text


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
        audio, output = pc.generate_pdf_to_podcast(text, model)
        encoded = base64.b64encode(audio).decode("utf-8")
        update_job_status(db, self.request.id, "Completed")
        index, chunks = store_embedded(output)
        serialized_index = faiss.serialize_index(index)
        redis_client.set(f"index:{self.request.id}", serialized_index.tobytes())
        redis_client.set(f"chunks:{self.request.id}", json.dumps(output))
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