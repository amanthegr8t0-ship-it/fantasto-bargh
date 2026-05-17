import re
import textwrap
from core.exceptions import ScriptGenerationError
from core.config import MAX_CHAR, CHUNK_SIZE, CONTEXT_SIZE
import logging

logger = logging.getLogger(__name__)

def clean_chunk(text):
    try:
        text = text.replace("\u2018", "'").replace("\u2019", "'")
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        text = re.sub(r"[^\x00-\x7f]", " ", text)
        logger.info("chunk cleaning succeded")
        return text
    except Exception as e:
        logger.error(f"Text Cleaning Failed {e}")
        raise ScriptGenerationError(f"Text Cleaning Failed {e}") from e

def chunk_text(text):

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current_index = ""
    
    previous_context = ""
    for sentence in sentences:
        if len(current_index) + len(sentence) < CHUNK_SIZE:
            current_index += sentence +" "

        else:
            if previous_context:
                new_content = previous_context + current_index
                chunks.append(new_content)
                
            else:
                
                chunks.append(current_index)
            whole_previous_chunk = current_index 
            previous_context = whole_previous_chunk[-CONTEXT_SIZE:]
            current_index = sentence + " "

        
    if current_index.strip():
        chunks.append(previous_context+current_index)

    logger.info(f"chunking completed, made {len(chunks)} chunks")

    return chunks

def create_audio_chunks(script_text):

    try:
        if not script_text.strip():
            raise ValueError("Cannot create audio chunks from empty text.")
        chunks = textwrap.wrap(script_text, width=MAX_CHAR, break_long_words=True)

        if not chunks:
            raise ValueError("Audio chunking produced no output.")
        
        logger.info(f"audio chunking completed, made {len(chunks)} audio chunks")
        return chunks
    
    except ValueError as e:
        logger.error(f"Chunk Creation Failed {e}")
        raise
    
    except Exception as e :
        logger.error(f"Chunk Creation Failed {e}")
        raise ScriptGenerationError(f"Chunk Creation Failed {e}") from e