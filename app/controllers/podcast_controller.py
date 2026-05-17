from Pipeline.orchestrator import PodcastPipeline
from Services import text_extraction as te

def generate_text_to_speech(user_input, model, on_progress2 = None):

    pipeline = PodcastPipeline(user_input)
    pipeline.initialize_pipeline()
    pipeline.tts_path_maker()
    pipeline.generate_audio(model, on_progress2=on_progress2)

    return pipeline.final_audio_bytes

    

def generate_pdf_to_podcast(user_input, model, on_progress1 = None, on_progress2 = None):

    pipeline = PodcastPipeline(user_input)
    pipeline.initialize_pipeline()
    pipeline.generate_script(on_progress1 = on_progress1)
    pipeline.generate_audio(model, on_progress2 = on_progress2)

    return pipeline.final_audio_bytes

def generate_text_from_pdf(pdf):

    return te.extract_text_from_pdf(pdf)
    
