import os
import click
from typing import Optional, Dict, Any
from pathlib import Path

def transcribe_audio_gemini_api(audio_path: str, model_name: str = 'gemini-2.5-flash-api',
                               language: Optional[str] = None, transcription_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Transcribe audio using Google Gemini API."""

    # Check dependencies
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise ImportError(
            "> Gemini API support requires missing dependencies\n\n"
            "> Quick fix:\n"
            "pip install google-genai\n\n"
            "> Note: You may need to restart your runtime after installation."
        )

    # Map model names to Gemini API model IDs
    model_mapping = {
        'gemini-2.5-pro-api': 'gemini-2.5-pro',
        'gemini-2.5-flash-api': 'gemini-2.5-flash',
        'gemini-2.5-flash-lite-api': 'gemini-2.5-flash-lite',
        'gemini-2.0-flash-api': 'gemini-2.0-flash'
    }

    if model_name not in model_mapping:
        raise ValueError(f"Unknown Gemini API model: {model_name}")

    api_model_id = model_mapping[model_name]

    # Get Gemini API key
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError(
            "> Google API key is required\n\n"
            "> Set your API key:\n"
            "export GOOGLE_API_KEY='your-api-key-here'\n\n"
            "> Get your API key from: https://aistudio.google.com/apikey"
        )

    # Initialize Gemini client
    client = genai.Client(api_key=api_key)

    # 20MB threshold for inline vs File API
    MAX_INLINE_SIZE = 20 * 1024 * 1024
    file_size = Path(audio_path).stat().st_size

    # Construct transcription prompt
    base_prompt = "Please transcribe this audio file. Provide only the transcription text, without any additional commentary or formatting."

    if transcription_prompt:
        base_prompt = f"{base_prompt} Additional context: {transcription_prompt}"

    if language:
        base_prompt = f"{base_prompt} The audio is in {language}."

    try:
        if file_size < MAX_INLINE_SIZE:
            # Use inline method for files under 20MB
            result = _transcribe_inline(client, audio_path, api_model_id, base_prompt)
        else:
            # Use File API for larger files
            result = _transcribe_with_file_api(client, audio_path, api_model_id, base_prompt, file_size)

        return _convert_gemini_to_whisper_format(result, language)

    except Exception as e:
        error_str = str(e).lower()
        if "api_key" in error_str or "unauthorized" in error_str or "permission" in error_str:
            raise Exception(
                "> Invalid Google API key\n\n"
                "> Check your API key:\n"
                "1. Visit https://aistudio.google.com/apikey\n"
                "2. Make sure your key is active\n"
                "3. Update your GOOGLE_API_KEY environment variable"
            )
        elif "quota" in error_str or "limit" in error_str:
            raise Exception(
                "> Gemini API quota exceeded\n\n"
                "> Check your usage:\n"
                "1. Visit https://aistudio.google.com/\n"
                "2. Check your API quota and limits"
            )
        else:
            raise Exception(f"Gemini API transcription failed: {e}")


def _transcribe_inline(client, audio_path: str, api_model_id: str, prompt: str) -> str:
    """Transcribe audio using inline method (for files <20MB)."""
    from google.genai import types

    # Determine MIME type based on file extension
    mime_type_map = {
        '.mp3': 'audio/mp3',
        '.wav': 'audio/wav',
        '.aac': 'audio/aac',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac',
        '.aiff': 'audio/aiff',
        '.m4a': 'audio/mp4'
    }

    file_ext = Path(audio_path).suffix.lower()
    mime_type = mime_type_map.get(file_ext, 'audio/mpeg')

    with click.progressbar(length=1, label='Transcribing with Gemini API (inline)') as bar:
        with open(audio_path, 'rb') as f:
            audio_bytes = f.read()

        response = client.models.generate_content(
            model=api_model_id,
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=mime_type
                )
            ]
        )
        bar.update(1)

    return response.text


def _transcribe_with_file_api(client, audio_path: str, api_model_id: str, prompt: str, file_size: int) -> str:
    """Transcribe audio using File API (for files ≥20MB)."""

    click.echo(f"> File size ({file_size / (1024*1024):.1f}MB) exceeds inline limit. Using File API...")

    with click.progressbar(length=2, label='Uploading to Gemini') as bar:
        # Upload file
        uploaded_file = client.files.upload(file=audio_path)
        bar.update(1)

        # Generate content with uploaded file
        response = client.models.generate_content(
            model=api_model_id,
            contents=[prompt, uploaded_file]
        )
        bar.update(1)

    return response.text


def _convert_gemini_to_whisper_format(gemini_text: str, language: Optional[str]) -> Dict[str, Any]:
    """Convert Gemini API response to Whisper-compatible format."""

    # Gemini returns plain text without detailed timestamps
    # Create a single segment for the entire transcription
    segments = [{
        'id': 0,
        'seek': 0,
        'start': 0.0,
        'end': 0.0,  # No timing information available from Gemini
        'text': gemini_text,
        'tokens': [],
        'temperature': 0.0,
        'avg_logprob': 0.0,
        'compression_ratio': 1.0,
        'no_speech_prob': 0.0
    }]

    return {
        'text': gemini_text,
        'segments': segments,
        'language': language if language else 'unknown'
    }


def is_gemini_api_model(model_name: str) -> bool:
    """Check if the model name corresponds to a Gemini API model."""
    gemini_api_models = [
        'gemini-2.5-pro-api',
        'gemini-2.5-flash-api',
        'gemini-2.5-flash-lite-api',
        'gemini-2.0-flash-api'
    ]
    return model_name in gemini_api_models


def check_gemini_api_setup() -> bool:
    """Check if Gemini API is properly configured."""
    return bool(os.environ.get('GOOGLE_API_KEY'))


def get_model_info(model_name: str) -> Dict[str, Any]:
    """Get information about a Gemini API model."""
    model_info = {
        'gemini-2.5-pro-api': {
            'api_id': 'gemini-2.5-pro',
            'description': 'Gemini 2.5 Pro - highest quality audio transcription',
            'features': ['high_accuracy', 'multiple_languages', 'large_context']
        },
        'gemini-2.5-flash-api': {
            'api_id': 'gemini-2.5-flash',
            'description': 'Gemini 2.5 Flash - fast and efficient transcription',
            'features': ['fast', 'cost_effective', 'multiple_languages']
        },
        'gemini-2.5-flash-lite-api': {
            'api_id': 'gemini-2.5-flash-lite',
            'description': 'Gemini 2.5 Flash Lite - lightweight transcription',
            'features': ['lightweight', 'cost_effective', 'fast']
        },
        'gemini-2.0-flash-api': {
            'api_id': 'gemini-2.0-flash',
            'description': 'Gemini 2.0 Flash - previous generation fast transcription',
            'features': ['fast', 'reliable']
        }
    }
    return model_info.get(model_name, {})
