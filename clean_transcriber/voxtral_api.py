import os
import requests
import click
from typing import Optional, Dict, Any

def transcribe_audio_voxtral_api(audio_path: str, model_name: str = 'voxtral-mini-latest', 
                                language: Optional[str] = None, transcription_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Transcribe audio using Mistral's Voxtral API."""
    
    api_key = os.environ.get('MISTRAL_API_KEY')
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is required for Voxtral API usage")
    
    # Map model names to API model identifiers
    model_mapping = {
        'voxtral-mini-latest': 'voxtral-mini-latest',
        'voxtral-small-latest': 'voxtral-small-latest'
    }
    
    api_model = model_mapping.get(model_name, model_name)
    
    url = 'https://api.mistral.ai/v1/audio/transcriptions'
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    # Prepare form data
    data = {
        'model': api_model
    }
    
    if language:
        data['language'] = language
    
    # Add timestamp granularities to get segment information
    data['timestamp_granularities[]'] = 'segment'
    
    # Open the audio file
    try:
        with open(audio_path, 'rb') as audio_file:
            files = {'file': audio_file}
            
            with click.progressbar(length=1, label='Transcribing via Mistral API') as bar:
                response = requests.post(url, headers=headers, data=data, files=files)
                bar.update(1)
                
    except FileNotFoundError:
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    if response.status_code != 200:
        try:
            error_detail = response.json().get('error', {}).get('message', 'Unknown error')
        except:
            error_detail = f"HTTP {response.status_code}"
        raise Exception(f"Mistral API error: {error_detail}")
    
    try:
        result = response.json()
    except ValueError:
        raise Exception("Invalid JSON response from Mistral API")
    
    # Convert Mistral API response format to match Whisper format
    whisper_format = _convert_to_whisper_format(result)
    
    return whisper_format


def _convert_to_whisper_format(mistral_result: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Mistral API response to Whisper-compatible format."""
    
    # Extract main text
    text = mistral_result.get('text', '')
    
    # Convert segments if available
    segments = []
    if 'segments' in mistral_result:
        for segment in mistral_result['segments']:
            # Convert to Whisper segment format
            whisper_segment = {
                'id': segment.get('id', 0),
                'seek': 0,  # Mistral doesn't provide seek info
                'start': segment.get('start', 0.0),
                'end': segment.get('end', 0.0),
                'text': segment.get('text', ''),
                'tokens': [],  # Mistral doesn't provide token info
                'temperature': 0.0,
                'avg_logprob': 0.0,
                'compression_ratio': 1.0,
                'no_speech_prob': 0.0
            }
            segments.append(whisper_segment)
    
    # Return in Whisper format
    return {
        'text': text,
        'segments': segments,
        'language': mistral_result.get('language', 'unknown')
    }


def is_voxtral_api_model(model_name: str) -> bool:
    """Check if the model name corresponds to a Voxtral API model."""
    voxtral_api_models = [
        'voxtral-mini-latest',
        'voxtral-small-latest',
        'voxtral-mini-2507',  # Direct API model name
        'voxtral-small-2507'  # Future direct API model name
    ]
    return model_name in voxtral_api_models


def check_voxtral_api_setup() -> bool:
    """Check if Voxtral API is properly configured."""
    return bool(os.environ.get('MISTRAL_API_KEY'))