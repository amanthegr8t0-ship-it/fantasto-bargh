import os
from dotenv import load_dotenv
from core.exceptions import ConfigurationError

load_dotenv()

def _require(key: str) -> str:
    value = os.getenv(key)
    if not value or not value.strip():
        raise ConfigurationError(
            f"Missing required environment variable: '{key}'\n"
            f"Add it to your .env file: {key}=your_value_here"
        )
    return value.strip()

NVIDIA_API_KEY = _require("NVIDIA_API_KEY")

CHUNK_SIZE = 1000
MAX_CHAR = 350
RIVA_URI = "grpc.nvcf.nvidia.com:443"
RIVA_FUNCTION_ID = "877104f7-e885-42b9-8de8-f6e4c6303969"
LANGUAGE = "en-US"
SAMPLE_HZ = 44100
TTS_VOICE_PREFIX = "Magpie-Multilingual.EN-US."

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
LLM_MODEL = "meta/llama-3.1-70b-instruct"
TEMPERATURE = 0.5
MAX_TOKEN = 500
CONTEXT_SIZE = 150
VOICE_OPTION = ["Jason","Aria"]
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")