from fastapi import FastAPI, Response, HTTPException, UploadFile, File
from pydantic import BaseModel
from controllers import podcast_controller as pc
from core.exceptions import ConfigurationError, AudioGenerationError, ScriptGenerationError, PDFExtractionError
import asyncio
from api.tasks import generate_podcast_task, generate_text_to_speech_task, celery_app
from celery.result import AsyncResult
import base64

app = FastAPI()
class PodcastRequest(BaseModel):
    text: str
    model : str

@app.post("/generate-text-to-speech")
async def generate_tts(request: PodcastRequest):
    try:
        job = generate_text_to_speech_task.delay(request.text, request.model)  # fires and forgets
        return {"job_id": job.id}
    except ConfigurationError:
        raise HTTPException (status_code= 500, detail="Something went wrong while connecting the server")
    except AudioGenerationError:
        raise HTTPException (status_code= 500, detail="Something went wrong while generating audio")
    except Exception as e:
        raise HTTPException (status_code= 500, detail="Something went wrong on our side")


@app.post("/generate-pdf-to-podcast")
async def generate_podcast(request: PodcastRequest):
    try:
        job = generate_podcast_task.delay(request.text, request.model)  # fires and forgets
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