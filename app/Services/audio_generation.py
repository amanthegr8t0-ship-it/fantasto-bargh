from utils import chunking as ch
import os
import pydub as pb
from core.exceptions import AudioGenerationError
from core.config import SAMPLE_HZ, LANGUAGE, TTS_VOICE_PREFIX
import logging

logger = logging.getLogger(__name__)

def generate_studio_audio(tem_dir,audio_chunk, select_model, tts_service,index):
    try:
        if audio_chunk.strip():
                
            response = user_selected_model(audio_chunk, tts_service, select_model)

            raw_audio = pb.AudioSegment(
            data=response.audio,
            sample_width=2,
            frame_rate = SAMPLE_HZ,
            channels = 1
            )
            output_path = os.path.join(tem_dir, f"podcast_part_{index}.wav")
            with open (output_path, "wb") as f:
                raw_audio.export(f, format="wav")

            logger.info("studio audio generaion successful.")
            
    except Exception as e :
        logger.error(f"Audio generation Failed. {e}")
        raise AudioGenerationError(f"Audio generation Failed. {e}") from e 

def export_the_audio(tem_dir, audio_chunks):

    try:
        combined_audio = pb.AudioSegment.empty()

        for index, audio_chunk in enumerate(audio_chunks):
            file_path = os.path.join(tem_dir, f"podcast_part_{index}.wav")
            if os.path.exists(file_path):
                audio_part = pb.AudioSegment.from_wav(file_path)

                combined_audio += audio_part
            else:
                raise RuntimeError(f"Audio file dosen't exists for {index + 1}")

        combined_audio.export(
            os.path.join(tem_dir, f"Final_Podcast.mp3"),
            format="mp3"
        )

        with open(os.path.join(tem_dir, "Final_Podcast.mp3"), "rb") as f:
        
            final_audio_bytes = f.read()
        logger.info("Audio export secceded.")
        return final_audio_bytes
    
    except RuntimeError as e:
        logger.error(f"Unexpected audio pipeline error: {e}")
        raise
    except Exception as e :
        logger.error(f"Unexpected audio pipeline error: {e}")
        raise AudioGenerationError(f"Unexpected audio pipeline error: {e}") from e

def user_selected_model(audio_chunk, tts_service, model = "Jason"):
    try:
        response = tts_service.synthesize(
            text= audio_chunk,
            language_code =LANGUAGE,
            voice_name= TTS_VOICE_PREFIX+model,
            sample_rate_hz= SAMPLE_HZ
        )
        logger.info("Model selection secceded.")
        return response
    except Exception as e:
        logger.error(f"Model Selection Failed {e}")
        raise AudioGenerationError(f"Model Selection Failed {e}") from e