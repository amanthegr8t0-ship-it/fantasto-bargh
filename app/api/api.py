from fastapi import FastAPI, Response, HTTPException, UploadFile, File
from pydantic import BaseModel
from controllers import podcast_controller as pc
from core.exceptions import ConfigurationError, AudioGenerationError, ScriptGenerationError, PDFExtractionError
import asyncio

app = FastAPI()
class PodcastRequest(BaseModel):
    text: str
    model : str

@app.post("/generate-text-to-speech")
async def generate_tts(request: PodcastRequest):
    try:
        output =await asyncio.to_thread( pc.generate_text_to_speech, request.text, request.model)
        return Response(content=output, media_type="audio/mpeg")
    except ConfigurationError:
        raise HTTPException (status_code= 500, detail="Something went wrong while connecting the server")
    except AudioGenerationError:
        raise HTTPException (status_code= 500, detail="Something went wrong while generating audio")
    except Exception as e:
        raise HTTPException (status_code= 500, detail="Something went wrong on our side")


@app.post("/generate-pdf-to-podcast")
async def generate_podcast(request: PodcastRequest):
    try:
        output =await asyncio.to_thread( pc.generate_pdf_to_podcast, request.text, request.model)
        return Response(content=output, media_type="audio/mpeg")
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
