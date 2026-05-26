from datetime import datetime
from fastapi import FastAPI, Response, HTTPException, UploadFile, File
from pydantic import BaseModel
from controllers import podcast_controller as pc
from core.exceptions import ConfigurationError, AudioGenerationError, ScriptGenerationError, PDFExtractionError
import asyncio
from api.tasks import generate_podcast_task, generate_text_to_speech_task, celery_app
from celery.result import AsyncResult
import base64
from core.database import SessionLocal, Job
import faiss
import json
from core.redis_client import redis_client
from Services.retrieval import fetch_embedded
from Services.llm_engine import request_transmission
import numpy as np


app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://172.29.80.223:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PodcastRequest(BaseModel):
    text: str
    model : str

class QuestionRequest(BaseModel):
    question: str
    job_id : str
    live_memory : str = ""

@app.post("/generate-text-to-speech")
async def generate_tts(request: PodcastRequest):
    try:
        job = generate_text_to_speech_task.delay(request.text, request.model)  # fires and forgets
        db = SessionLocal()
        db.add(Job(job_id=job.id, status="PENDING", created_at=datetime.now()))
        db.commit()
        db.close()
        return {"job_id": job.id}
    except ConfigurationError:
        raise HTTPException (status_code= 500, detail="Something went wrong while connecting the server")
    except AudioGenerationError:
        raise HTTPException (status_code= 500, detail="Something went wrong while generating audio")
    except Exception as e:
        raise HTTPException (status_code= 500, detail=f"Something went wrong on our side {e}")


@app.post("/generate-pdf-to-podcast")
async def generate_podcast(request: PodcastRequest):
    try:
        job = generate_podcast_task.delay(request.text, request.model)  # fires and forgets
        db = SessionLocal()
        db.add(Job(job_id=job.id, status="Pending", created_at=datetime.now()))
        db.commit()
        db.close()
        return {"job_id": job.id}
    except ScriptGenerationError:
        raise HTTPException (status_code= 500, detail="Something went wrong while generating script")
    except ConfigurationError:
        raise HTTPException (status_code= 500, detail="Something went wrong while connecting the server")
    except AudioGenerationError:
        raise HTTPException (status_code= 500, detail="Something went wrong while generating audio")
    except Exception as e:
        raise HTTPException (status_code= 500, detail="Something went wrong on our side")
    
@app.post("/extract-pdf-text")
async def extract_text_pdf(file: UploadFile = File(...)):
    try:
        content = await file.read()
        output = await asyncio.to_thread(pc.generate_text_from_pdf, content)
        return Response(content=output, media_type="text/plain")
    except ValueError:
        raise HTTPException(status_code=500, detail="PDF appears to be empty")
    except PDFExtractionError:
        raise HTTPException(status_code=500, detail="Something went wrong while extraction from pdf.")
    except Exception as e:
        raise HTTPException (status_code= 500, detail="Something went wrong on our side")
    
@app.post("/ask-question")
async def ask_question(request: QuestionRequest):
    try:
        bytes = redis_client.get(f"index:{request.job_id}")
        if not bytes:
            raise HTTPException(status_code=500, detail="Please wait for the podcast to generate to ask the question.")
        f_index = faiss.deserialize_index(np.frombuffer(bytes, dtype=np.uint8))
        original_chunk = json.loads(redis_client.get(f"chunks:{request.job_id}"))
        relevant_chunk = fetch_embedded(f_index,original_chunk, request.question)
        response = request_transmission("\n\n".join(relevant_chunk), quest=request.question, task="question")
        memo_system = request_transmission(request.live_memory,response, task="memo_add")
        return {"answer": response, "live_memory": memo_system}
    except Exception as e:
        raise
    

@app.get("/job/podcast/{job_id}")
async def get_podcast_job(job_id : str):
    result = AsyncResult(job_id, app=celery_app)
    if result.ready():
        audio_bytes = base64.b64decode(result.get())
        return Response(content=audio_bytes, media_type="audio/mpeg")
    return {"Status" : result.status}

@app.get("/job/tts/{job_id}")
async def get_tts_job(job_id : str):
    result = AsyncResult(job_id, app=celery_app)
    if result.ready():
        audio_bytes = base64.b64decode(result.get())
        return Response(content=audio_bytes, media_type="audio/mpeg")
    return {"status" : result.status}