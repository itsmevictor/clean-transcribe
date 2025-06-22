import whisper
import warnings
import click

def transcribe_audio(audio_path, model_name='base', language=None):
    """Transcribe audio using OpenAI Whisper."""
    # Suppress FP16 warnings
    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
    
    # Load the Whisper model
    with click.progressbar(length=1, label='Loading model') as bar:
        model = whisper.load_model(model_name)
        bar.update(1)
    
    # Transcribe options
    options = {
        'task': 'transcribe',
        'verbose': False,
    }
    
    if language:
        options['language'] = language
    
    # Perform transcription
    result = model.transcribe(audio_path, **options)
    
    return result