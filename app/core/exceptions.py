class PodcastAppError(Exception):pass
class AudioGenerationError(PodcastAppError):pass
class ConfigurationError(PodcastAppError):pass
class PDFExtractionError(PodcastAppError):pass
class ScriptGenerationError(PodcastAppError):pass