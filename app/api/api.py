from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from controllers import podcast_controller as pc
from core.exceptions import ConfigurationError, AudioGenerationError, ScriptGenerationError

app = FastAPI()
class PodcastRequest(BaseModel):
    text: str
    model : str

@app.post("/generate-text-to-speech")
def generate_tts(request: PodcastRequest):
    try:
        output = pc.generate_text_to_speech(request.text, request.model)
        return Response(content=output, media_type="audio/mpeg")
    except ConfigurationError:
        raise HTTPException (status_code= 500, detail="Something went wrong while connecting the server")
    except AudioGenerationError:
        raise HTTPException (status_code= 500, detail="Something went wrong while generating audio")
    except Exception as e:
        raise HTTPException (status_code= 500, detail="Something went wrong on our side")


@app.post("/generate-pdf-to-podcast")
def generate_podcast(request: PodcastRequest):
    try:
        output = pc.generate_pdf_to_podcast(request.text, request.model)
        return Response(content=output, media_type="audio/mpeg")
    except ScriptGenerationError:
        raise HTTPException (status_code= 500, detail="Something went wrong while generating script")
    except ConfigurationError:
        raise HTTPException (status_code= 500, detail="Something went wrong while connecting the server")
    except AudioGenerationError:
        raise HTTPException (status_code= 500, detail="Something went wrong while generating audio")
    except Exception as e:
        raise HTTPException (status_code= 500, detail="Something went wrong on our side")