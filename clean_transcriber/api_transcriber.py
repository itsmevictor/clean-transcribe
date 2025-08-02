import os
import tempfile
from pathlib import Path
from pydub import AudioSegment
import click
from openai import OpenAI

# 25MB file size limit for OpenAI API
MAX_FILE_SIZE = 25 * 1024 * 1024

# Available OpenAI models
OPENAI_MODELS = ['whisper-1', 'gpt-4o-transcribe', 'gpt-4o-mini-transcribe']

def get_openai_client(api_key=None):
    """Initialize OpenAI client with API key from parameter or environment."""
    if api_key:
        return OpenAI(api_key=api_key)
    elif os.getenv('OPENAI_API_KEY'):
        return OpenAI()
    else:
        raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass --api-key parameter.")

def get_file_size(file_path):
    """Get file size in bytes."""
    return Path(file_path).stat().st_size

def chunk_audio_file(file_path, chunk_duration_ms=10 * 60 * 1000):  # 10 minutes default
    """Split audio file into chunks to stay under API size limit."""
    audio = AudioSegment.from_file(file_path)
    chunks = []
    
    # Calculate chunk size to stay under 25MB limit
    total_duration = len(audio)
    estimated_size_per_ms = get_file_size(file_path) / total_duration
    safe_chunk_duration = min(chunk_duration_ms, int(MAX_FILE_SIZE * 0.8 / estimated_size_per_ms))
    
    for i in range(0, total_duration, safe_chunk_duration):
        chunk = audio[i:i + safe_chunk_duration]
        chunks.append(chunk)
    
    return chunks

def transcribe_chunk(client, chunk_data, chunk_path, model_name, language=None, transcription_prompt=None):
    """Transcribe a single audio chunk using OpenAI API."""
    try:
        # Save chunk to temporary file
        chunk_data.export(chunk_path, format="mp3")
        
        # Prepare transcription parameters
        transcribe_params = {
            'file': open(chunk_path, 'rb'),
            'model': model_name,
        }
        
        # Add optional parameters
        if language:
            transcribe_params['language'] = language
        
        if transcription_prompt:
            transcribe_params['prompt'] = transcription_prompt
        
        # For whisper-1, we can get detailed timing information
        if model_name == 'whisper-1':
            transcribe_params['response_format'] = 'verbose_json'
            transcribe_params['timestamp_granularities'] = ['segment']
        
        # Make API call
        result = client.audio.transcriptions.create(**transcribe_params)
        
        # Close file handle
        transcribe_params['file'].close()
        
        return result
        
    except Exception as e:
        if 'file' in transcribe_params and not transcribe_params['file'].closed:
            transcribe_params['file'].close()
        raise e

def merge_chunk_results(chunk_results, model_name):
    """Merge transcription results from multiple chunks."""
    if not chunk_results:
        return {"text": ""}
    
    # For single chunk, return as-is
    if len(chunk_results) == 1:
        result = chunk_results[0]
        # Convert API response to dict format expected by the rest of the pipeline
        if hasattr(result, 'text'):
            if model_name == 'whisper-1' and hasattr(result, 'segments'):
                return {
                    'text': result.text,
                    'segments': [
                        {
                            'text': seg['text'],
                            'start': seg['start'],
                            'end': seg['end']
                        } for seg in result.segments
                    ]
                }
            else:
                return {'text': result.text}
        return result
    
    # Merge multiple chunks
    merged_text = ""
    merged_segments = []
    time_offset = 0.0
    
    for i, result in enumerate(chunk_results):
        if hasattr(result, 'text'):
            text = result.text
        else:
            text = result.get('text', '')
        
        # Add space between chunks
        if i > 0:
            merged_text += " "
        merged_text += text
        
        # Handle segments for whisper-1
        if model_name == 'whisper-1' and hasattr(result, 'segments'):
            for segment in result.segments:
                merged_segments.append({
                    'text': segment['text'],
                    'start': segment['start'] + time_offset,
                    'end': segment['end'] + time_offset
                })
            
            # Update time offset for next chunk (estimate based on chunk duration)
            if result.segments:
                time_offset = merged_segments[-1]['end']
        else:
            # Estimate chunk duration for time offset (10 minutes default)
            time_offset += 600.0  # 10 minutes in seconds
    
    # Return merged result
    merged_result = {'text': merged_text}
    if merged_segments:
        merged_result['segments'] = merged_segments
    
    return merged_result

def transcribe_audio_api(audio_path, model_name='whisper-1', language=None, transcription_prompt=None, api_key=None):
    """Transcribe audio using OpenAI API."""
    if model_name not in OPENAI_MODELS:
        raise ValueError(f"Model {model_name} not supported. Available models: {OPENAI_MODELS}")
    
    # Initialize OpenAI client
    client = get_openai_client(api_key)
    
    # Check file size
    file_size = get_file_size(audio_path)
    
    if file_size <= MAX_FILE_SIZE:
        # File is small enough, transcribe directly
        with click.progressbar(length=1, label='Transcribing with OpenAI API') as bar:
            with open(audio_path, 'rb') as audio_file:
                transcribe_params = {
                    'file': audio_file,
                    'model': model_name,
                }
                
                if language:
                    transcribe_params['language'] = language
                
                if transcription_prompt:
                    transcribe_params['prompt'] = transcription_prompt
                
                # For whisper-1, get detailed timing information
                if model_name == 'whisper-1':
                    transcribe_params['response_format'] = 'verbose_json'
                    transcribe_params['timestamp_granularities'] = ['segment']
                
                result = client.audio.transcriptions.create(**transcribe_params)
                bar.update(1)
        
        # Convert API response to expected format
        if hasattr(result, 'text'):
            if model_name == 'whisper-1' and hasattr(result, 'segments'):
                return {
                    'text': result.text,
                    'segments': [
                        {
                            'text': seg['text'],
                            'start': seg['start'],
                            'end': seg['end']
                        } for seg in result.segments
                    ]
                }
            else:
                return {'text': result.text}
        return result
    
    else:
        # File is too large, need to chunk it
        click.echo(f"⚠️  File size ({file_size / (1024*1024):.1f}MB) exceeds API limit. Splitting into chunks...")
        
        chunks = chunk_audio_file(audio_path)
        chunk_results = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with click.progressbar(length=len(chunks), label='Transcribing chunks') as bar:
                for i, chunk in enumerate(chunks):
                    chunk_path = os.path.join(temp_dir, f"chunk_{i}.mp3")
                    
                    # For context continuity, include previous chunk's ending in the prompt
                    chunk_prompt = transcription_prompt
                    if i > 0 and chunk_results and transcription_prompt:
                        prev_text = chunk_results[-1].text if hasattr(chunk_results[-1], 'text') else chunk_results[-1].get('text', '')
                        # Get last few words for context
                        prev_words = prev_text.split()[-10:] if prev_text else []
                        if prev_words:
                            chunk_prompt = f"Previous context: {' '.join(prev_words)}. {transcription_prompt}"
                    
                    result = transcribe_chunk(client, chunk, chunk_path, model_name, language, chunk_prompt)
                    chunk_results.append(result)
                    bar.update(1)
        
        # Merge results
        return merge_chunk_results(chunk_results, model_name)