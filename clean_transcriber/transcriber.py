import whisper
import warnings
import click
from typing import Optional, Dict, Any

def transcribe_audio(audio_path: str, model_name: str = 'base', language: Optional[str] = None, 
                    transcription_prompt: Optional[str] = None, auto_download: bool = False) -> Dict[str, Any]:
    """
    Transcribe audio using the appropriate provider based on model name.
    
    Supports:
    - Whisper models: tiny, base, small, medium, large, turbo
    - Voxtral API models: voxtral-mini-latest, voxtral-small-latest  
    - Voxtral Local models: voxtral-mini-local, voxtral-small-local
    """
    
    # Route to appropriate provider based on model name
    if is_voxtral_api_model(model_name):
        return transcribe_audio_voxtral_api(audio_path, model_name, language, transcription_prompt)
    elif is_voxtral_local_model(model_name):
        return transcribe_audio_voxtral_local(audio_path, model_name, language, transcription_prompt, auto_download)
    else:
        return transcribe_audio_whisper(audio_path, model_name, language, transcription_prompt)


def transcribe_audio_whisper(audio_path: str, model_name: str = 'base', language: Optional[str] = None, 
                           transcription_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Transcribe audio using OpenAI Whisper."""
    # Suppress FP16 warnings
    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
    
    # Load the Whisper model
    with click.progressbar(length=1, label='Loading Whisper model') as bar:
        model = whisper.load_model(model_name)
        bar.update(1)
    
    # Transcribe options
    options = {
        'task': 'transcribe',
        'verbose': False,
    }
    
    if language:
        options['language'] = language
    
    if transcription_prompt:
        options['prompt'] = transcription_prompt
    
    # Perform transcription
    result = model.transcribe(audio_path, **options)
    
    return result


def is_voxtral_api_model(model_name: str) -> bool:
    """Check if model should use Voxtral API."""
    try:
        from .voxtral_api import is_voxtral_api_model
        return is_voxtral_api_model(model_name)
    except ImportError:
        return False


def is_voxtral_local_model(model_name: str) -> bool:
    """Check if model should use local Voxtral."""
    try:
        from .voxtral_local import is_voxtral_local_model
        return is_voxtral_local_model(model_name)
    except ImportError:
        return False


def transcribe_audio_voxtral_api(audio_path: str, model_name: str, language: Optional[str], 
                               transcription_prompt: Optional[str]) -> Dict[str, Any]:
    """Route to Voxtral API transcription."""
    try:
        from .voxtral_api import transcribe_audio_voxtral_api
        return transcribe_audio_voxtral_api(audio_path, model_name, language, transcription_prompt)
    except ImportError as e:
        raise ImportError(f"Voxtral API support not available: {e}")


def transcribe_audio_voxtral_local(audio_path: str, model_name: str, language: Optional[str], 
                                 transcription_prompt: Optional[str], auto_download: bool) -> Dict[str, Any]:
    """Route to local Voxtral transcription."""
    try:
        from .voxtral_local import transcribe_audio_voxtral_local
        return transcribe_audio_voxtral_local(audio_path, model_name, language, transcription_prompt, auto_download)
    except ImportError as e:
        raise ImportError(f"Local Voxtral support not available: {e}")


def get_available_models() -> Dict[str, list]:
    """Get all available models grouped by provider."""
    models = {
        'whisper': ['tiny', 'base', 'small', 'medium', 'large', 'turbo'],
        'voxtral_api': [],
        'voxtral_local': []
    }
    
    # Check Voxtral API availability
    try:
        from .voxtral_api import check_voxtral_api_setup
        if check_voxtral_api_setup():
            models['voxtral_api'] = ['voxtral-mini-latest', 'voxtral-small-latest']
    except ImportError:
        pass
    
    # Check local Voxtral availability
    try:
        from .voxtral_local import check_voxtral_local_setup
        if check_voxtral_local_setup():
            models['voxtral_local'] = ['voxtral-mini-local', 'voxtral-small-local']
    except ImportError:
        pass
    
    return models