import os
import tempfile
import click
from typing import Optional, Dict, Any
from pathlib import Path

def transcribe_audio_openai_api(audio_path: str, model_name: str = 'whisper-1-api', 
                               language: Optional[str] = None, transcription_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Transcribe audio using OpenAI API."""
    
    # Check dependencies
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "> OpenAI API support requires missing dependencies\n\n"
            "> Quick fix:\n"
            "pip install openai\n\n"
            "> Note: You may need to restart your runtime after installation."
        )
    
    try:
        from pydub import AudioSegment
    except ImportError:
        raise ImportError(
            "> OpenAI API support requires missing dependencies\n\n"
            "> Quick fix:\n"
            "pip install pydub\n\n"
            "> Note: You may need to restart your runtime after installation."
        )
    
    # Map model names to OpenAI API model IDs
    model_mapping = {
        'whisper-1-api': 'whisper-1',
        'gpt-4o-transcribe-api': 'gpt-4o-transcribe', 
        'gpt-4o-mini-transcribe-api': 'gpt-4o-mini-transcribe'
    }
    
    if model_name not in model_mapping:
        raise ValueError(f"Unknown OpenAI API model: {model_name}")
    
    api_model_id = model_mapping[model_name]
    
    # Get OpenAI API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError(
            "> OpenAI API key is required\n\n"
            "> Set your API key:\n"
            "export OPENAI_API_KEY='your-api-key-here'\n\n"
            "> Get your API key from: https://platform.openai.com/api-keys"
        )
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # 25MB file size limit for OpenAI API
    MAX_FILE_SIZE = 25 * 1024 * 1024
    file_size = Path(audio_path).stat().st_size
    
    try:
        if file_size <= MAX_FILE_SIZE:
            # File is small enough, transcribe directly
            return _transcribe_single_file(client, audio_path, api_model_id, language, transcription_prompt)
        else:
            # File is too large, need to chunk it
            return _transcribe_chunked_file(client, audio_path, api_model_id, language, transcription_prompt, file_size)
            
    except Exception as e:
        error_str = str(e).lower()
        if "invalid_api_key" in error_str or "unauthorized" in error_str:
            raise Exception(
                "> Invalid OpenAI API key\n\n"
                "> Check your API key:\n"
                "1. Visit https://platform.openai.com/api-keys\n"
                "2. Make sure your key is active and has credits\n"
                "3. Update your OPENAI_API_KEY environment variable"
            )
        elif "quota" in error_str or "billing" in error_str:
            raise Exception(
                "> OpenAI API quota exceeded or billing issue\n\n"
                "> Check your account:\n"
                "1. Visit https://platform.openai.com/account/billing\n"
                "2. Add credits or check your usage limits"
            )
        else:
            raise Exception(f"OpenAI API transcription failed: {e}")


def _transcribe_single_file(client, audio_path: str, api_model_id: str, language: Optional[str], 
                           transcription_prompt: Optional[str]) -> Dict[str, Any]:
    """Transcribe a single audio file using OpenAI API."""
    
    with click.progressbar(length=1, label='Transcribing with OpenAI API') as bar:
        with open(audio_path, 'rb') as audio_file:
            transcribe_params = {
                'file': audio_file,
                'model': api_model_id,
            }
            
            if language:
                transcribe_params['language'] = language
            
            if transcription_prompt:
                transcribe_params['prompt'] = transcription_prompt
            
            # For whisper-1, get detailed timing information
            if api_model_id == 'whisper-1':
                transcribe_params['response_format'] = 'verbose_json'
                transcribe_params['timestamp_granularities'] = ['segment']
            
            result = client.audio.transcriptions.create(**transcribe_params)
            bar.update(1)
    
    return _convert_openai_to_whisper_format(result, api_model_id)


def _transcribe_chunked_file(client, audio_path: str, api_model_id: str, language: Optional[str], 
                           transcription_prompt: Optional[str], file_size: int) -> Dict[str, Any]:
    """Transcribe a large audio file by splitting it into chunks."""
    
    click.echo(f"> File size ({file_size / (1024*1024):.1f}MB) exceeds API limit. Splitting into chunks...")
    
    from pydub import AudioSegment
    
    # Load and chunk audio
    audio = AudioSegment.from_file(audio_path)
    
    # Calculate safe chunk duration (10 minutes default, but adjust for file size)
    MAX_FILE_SIZE = 25 * 1024 * 1024
    total_duration = len(audio)
    estimated_size_per_ms = file_size / total_duration
    safe_chunk_duration = min(10 * 60 * 1000, int(MAX_FILE_SIZE * 0.8 / estimated_size_per_ms))  # 10 minutes or smaller
    
    # Create chunks
    chunks = []
    for i in range(0, total_duration, safe_chunk_duration):
        chunk = audio[i:i + safe_chunk_duration]
        chunks.append(chunk)
    
    # Transcribe chunks
    chunk_results = []
    with tempfile.TemporaryDirectory() as temp_dir:
        with click.progressbar(length=len(chunks), label='Transcribing chunks') as bar:
            for i, chunk in enumerate(chunks):
                chunk_path = os.path.join(temp_dir, f"chunk_{i}.mp3")
                
                # Export chunk to file
                with open(chunk_path, 'wb') as f:
                    chunk.export(f, format="mp3")
                
                # For context continuity, include previous chunk's ending in the prompt
                chunk_prompt = transcription_prompt
                if i > 0 and chunk_results and transcription_prompt:
                    prev_result = chunk_results[-1]
                    prev_text = prev_result.get('text', '')
                    # Get last few words for context
                    prev_words = prev_text.split()[-10:] if prev_text else []
                    if prev_words:
                        chunk_prompt = f"Previous context: {' '.join(prev_words)}. {transcription_prompt}"
                
                # Transcribe chunk
                with open(chunk_path, 'rb') as chunk_file:
                    transcribe_params = {
                        'file': chunk_file,
                        'model': api_model_id,
                    }
                    
                    if language:
                        transcribe_params['language'] = language
                    
                    if chunk_prompt:
                        transcribe_params['prompt'] = chunk_prompt
                    
                    if api_model_id == 'whisper-1':
                        transcribe_params['response_format'] = 'verbose_json'
                        transcribe_params['timestamp_granularities'] = ['segment']
                    
                    result = client.audio.transcriptions.create(**transcribe_params)
                
                chunk_results.append(_convert_openai_to_whisper_format(result, api_model_id))
                bar.update(1)
    
    # Merge chunk results
    return _merge_chunk_results(chunk_results, safe_chunk_duration / 1000.0)  # Convert ms to seconds


def _convert_openai_to_whisper_format(openai_result, api_model_id: str) -> Dict[str, Any]:
    """Convert OpenAI API response to Whisper-compatible format."""
    
    # Handle different response formats
    if hasattr(openai_result, 'text'):
        text = openai_result.text
        
        # If we have segments (whisper-1 with verbose_json)
        if api_model_id == 'whisper-1' and hasattr(openai_result, 'segments'):
            segments = []
            for seg in openai_result.segments:
                whisper_segment = {
                    'id': seg.get('id', 0),
                    'seek': seg.get('seek', 0),
                    'start': seg.get('start', 0.0),
                    'end': seg.get('end', 0.0),
                    'text': seg.get('text', ''),
                    'tokens': seg.get('tokens', []),
                    'temperature': seg.get('temperature', 0.0),
                    'avg_logprob': seg.get('avg_logprob', 0.0),
                    'compression_ratio': seg.get('compression_ratio', 1.0),
                    'no_speech_prob': seg.get('no_speech_prob', 0.0)
                }
                segments.append(whisper_segment)
            
            return {
                'text': text,
                'segments': segments,
                'language': getattr(openai_result, 'language', 'unknown')
            }
        else:
            # Simple text response, create a single segment
            segments = [{
                'id': 0,
                'seek': 0,
                'start': 0.0,
                'end': 0.0,  # We don't have timing information for non-whisper models
                'text': text,
                'tokens': [],
                'temperature': 0.0,
                'avg_logprob': 0.0,
                'compression_ratio': 1.0,
                'no_speech_prob': 0.0
            }]
            
            return {
                'text': text,
                'segments': segments,
                'language': 'unknown'
            }
    else:
        # Fallback for unexpected response format
        return {
            'text': str(openai_result),
            'segments': [],
            'language': 'unknown'
        }


def _merge_chunk_results(chunk_results: list, chunk_duration_seconds: float) -> Dict[str, Any]:
    """Merge transcription results from multiple chunks."""
    
    if not chunk_results:
        return {"text": "", "segments": [], "language": "unknown"}
    
    # For single chunk, return as-is
    if len(chunk_results) == 1:
        return chunk_results[0]
    
    # Merge multiple chunks
    merged_text = ""
    merged_segments = []
    time_offset = 0.0
    
    for i, result in enumerate(chunk_results):
        text = result.get('text', '')
        
        # Add space between chunks
        if i > 0 and merged_text and text:
            merged_text += " "
        merged_text += text
        
        # Handle segments with time offset
        segments = result.get('segments', [])
        for segment in segments:
            merged_segment = segment.copy()
            merged_segment['start'] = segment['start'] + time_offset
            merged_segment['end'] = segment['end'] + time_offset
            merged_segments.append(merged_segment)
        
        # Update time offset for next chunk
        if segments:
            # Use the actual end time of the last segment
            time_offset = merged_segments[-1]['end']
        else:
            # Estimate based on chunk duration
            time_offset += chunk_duration_seconds
    
    return {
        'text': merged_text,
        'segments': merged_segments,
        'language': chunk_results[0].get('language', 'unknown')
    }


def is_openai_api_model(model_name: str) -> bool:
    """Check if the model name corresponds to an OpenAI API model."""
    openai_api_models = [
        'whisper-1-api',
        'gpt-4o-transcribe-api', 
        'gpt-4o-mini-transcribe-api'
    ]
    return model_name in openai_api_models


def check_openai_api_setup() -> bool:
    """Check if OpenAI API dependencies are available."""
    try:
        from openai import OpenAI
        from pydub import AudioSegment
        return True
    except ImportError:
        return False


def get_model_info(model_name: str) -> Dict[str, Any]:
    """Get information about an OpenAI API model."""
    model_info = {
        'whisper-1-api': {
            'api_id': 'whisper-1',
            'description': 'OpenAI Whisper via API - fast, accurate transcription with timestamps',
            'features': ['timestamps', 'multiple_languages', 'prompts']
        },
        'gpt-4o-transcribe-api': {
            'api_id': 'gpt-4o-transcribe', 
            'description': 'GPT-4o transcription - highest quality understanding',
            'features': ['high_accuracy', 'context_aware']
        },
        'gpt-4o-mini-transcribe-api': {
            'api_id': 'gpt-4o-mini-transcribe',
            'description': 'GPT-4o Mini transcription - cost-effective option',
            'features': ['cost_effective', 'good_accuracy']
        }
    }
    return model_info.get(model_name, {})