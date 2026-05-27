from enum import Enum 
from utils import chunking as ch
from Services import llm_engine as Ai_eg
import tempfile
from Services import audio_generation as ag
from core.exceptions import *   
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from core.config import CONTEXT_SIZE

logger = logging.getLogger(__name__)

class PipelineState(Enum):
    IDLE = "idle"
    GENERATING_SCRIPT = "generating_script"
    SCRIPT_READY = "script_ready"
    GENERATING_AUDIO = "generating_audio"
    DONE = "done"
    FAILED = "failed"
class PodcastPipeline:
    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.chunks = []

        self.state = PipelineState.IDLE

        self.full_podcast_script = ""

        self.final_audio_bytes = None

        self.last_error = None

        self.allchunks = None


    def initialize_pipeline(self):

        try:
            self.state = PipelineState.GENERATING_SCRIPT
            self.chunks = ch.chunk_text(self.raw_text)
            logger.info(f"chunking succeded, created {len(self.chunks)} chunks ")

        except Exception as e :
            self.last_error = str(e)
            self.state = PipelineState.FAILED
            logger.error(f"chunking failed : {e}")
            raise

    def generate_script(self,on_progress1=None):
        if self.state != PipelineState.GENERATING_SCRIPT:
            raise RuntimeError(f"Cannot generate script from state: {self.state}")
        
        previous_context = ""
        for index, chunk in enumerate(self.chunks):
            current_index= index + 1
            if on_progress1 is not None:
                on_progress1(current_index, len(self.chunks))
            try:
                generated_script = Ai_eg.request_transmission(previous_context+chunk)
                self.full_podcast_script += generated_script
                previous_context = generated_script[-CONTEXT_SIZE:]
            
            except Exception as e:
                self.state = PipelineState.FAILED
                self.last_error = f"Script generation failed on section {index + 1}: {e}"
                logger.error(f"script generation failed : {e}")
                raise ScriptGenerationError(self.last_error) from e
            
        logger.info(f"script generation succeded")
        self.state = PipelineState.SCRIPT_READY

    def tts_path_maker(self):
        if self.state != PipelineState.GENERATING_SCRIPT:
            logger.error(f"Cannot generate script from state: {self.state}")
            raise RuntimeError(f"Cannot generate script from state: {self.state}")
        # self.full_podcast_script=ch.chunk_text(self.raw_text)
        self.full_podcast_script=self.raw_text
        self.state = PipelineState.SCRIPT_READY
        logger.info("path making succeded")

    def generate_audio(self, select_model, on_progress2 = None):
        if self.state != PipelineState.SCRIPT_READY:
            raise RuntimeError(f"Cannot generate audio from state: {self.state}")
        
        self.state = PipelineState.GENERATING_AUDIO
        try:
            clean_text = ch.clean_chunk(self.full_podcast_script)
            self.allchunks = ch.create_audio_chunks(clean_text)
            tts_service = Ai_eg.authorization()
            with  tempfile.TemporaryDirectory() as tem_dir:
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future_to_index = {
                        executor.submit(
                            ag.generate_studio_audio, 
                             tem_dir,
                            audio_chunk, 
                            select_model,
                            tts_service, 
                            index
                        ) : index for index, audio_chunk in enumerate(self.allchunks)
                    }
                    completed_count = 0 
                    for future in as_completed(future_to_index):
                        index = future_to_index[future]
                        try:
                            future.result()
                            completed_count += 1
                            if on_progress2:
                                on_progress2(completed_count, len(self.allchunks))
                        except Exception as e:
                            logger.error(f"thread for audio_chunk {index+1} failed: {e}")
                            raise AudioGenerationError(f"Audio generation failed for chunk {index+1}: {e}") from e


                self.final_audio_bytes = ag.export_the_audio(tem_dir, self.allchunks)
            self.state = PipelineState.DONE
            logger.info(f"audio generation succeded, Generated {len(self.allchunks)} audio packages")
            return self.final_audio_bytes, self.allchunks

        except Exception as e:
            self.state = PipelineState.FAILED
            self.last_error = f"Audio Generation Failed {str(e)}"
            logger.error(f"audio generation failed : {e}")
            raise AudioGenerationError(self.last_error) from e
        
    