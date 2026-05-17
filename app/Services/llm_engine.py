
import requests
import riva.client
from core.config import NVIDIA_API_KEY, NVIDIA_API_URL, LLM_MODEL, TEMPERATURE, MAX_TOKEN, RIVA_URI, RIVA_FUNCTION_ID
from core.exceptions import ScriptGenerationError

def request_transmission(chunk):

    prompt = f"""
    Turn the following PDF content into an engaging podcast-style explanation.

    Rules:
    - Make it conversational
    - Make it beginner friendly
    - Explain concepts naturally
    - Use simple language
    - Sound like a podcast host teaching listeners
    - Add excitement and smooth transitions
    - Avoid robotic explanations
    - CRITICAL: DO NOT write stage directions, sound effects, or speaker labels.
    - CRITICAL: Do not use brackets like [soft music] or (laughs). Write ONLY the spoken words.

    PDF Content:

    {chunk}
    """

    url = NVIDIA_API_URL

    headers = {
    "Authorization": f"Bearer {NVIDIA_API_KEY}",
    "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKEN
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()

        chunk_answer = result["choices"][0]["message"]["content"]
        
        chunk_podcast_script = chunk_answer + "\n\n"
        return chunk_podcast_script
    
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"NVIDIA API request failed (HTTP {e.response.status_code}): {e}") from e
    except requests.exceptions.ConnectionError as e :
        raise RuntimeError(f"Could not reach NVIDIA API — check your connection: {e}") from e
    except (KeyError,IndexError) as e:
        raise RuntimeError(f"Unexpected API response structure: {e}") from e
    except Exception as e:
        raise ScriptGenerationError(f"Script generation failed: {e}") from e

def authorization():
    auth = riva.client.Auth(
                uri= RIVA_URI,
                use_ssl = True,
                metadata_args =[("function-id", RIVA_FUNCTION_ID),("authorization", f"Bearer {NVIDIA_API_KEY}")]
            )
    tts_service = riva.client.SpeechSynthesisService(auth)
    return tts_service