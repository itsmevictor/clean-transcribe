#!/usr/bin/env python3
import click
import os
import tempfile
from pathlib import Path
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup, MutuallyExclusiveOptionGroup
from .downloader import download_audio
from .extractor import extract_audio
from .transcriber import transcribe_audio
from .formatter import format_output
from .cleaner import clean_long_transcript
from .trimmer import trim_audio

@click.command()
@click.argument('input_path', metavar='<URL or local path>')

# Output Options
@optgroup.group('Output Options')
@optgroup.option('--output', '-o', default=None, help='Output file path. Default for YouTube videos is a shortened, snake-cased version of the video title. Default for local files is the input filename with a new extension.')
@optgroup.option('--format', '-f', 'output_format', default='txt', 
              type=click.Choice(['txt', 'srt', 'vtt']), help='Output format (default: txt)')
@optgroup.option('--keep-audio', is_flag=True, help='Keep audio file (if downloaded)')
@optgroup.option('--save-raw', is_flag=True, help='Also save raw transcript before cleaning.')

# Transcription Options
@optgroup.group('Transcription Options', help='')
@optgroup.option('--model', '-m', default='whisper-small', 
              type=click.Choice([
                  # Whisper models (local)
                  'whisper-tiny', 'whisper-base', 'whisper-small', 'whisper-medium', 'whisper-large', 'whisper-turbo',
                  # OpenAI API models
                  'whisper-1-api', 'gpt-4o-transcribe-api', 'gpt-4o-mini-transcribe-api',
                  # Voxtral API models
                  'voxtral-mini-api', 'voxtral-small-api',
                  # Voxtral Local models
                  'voxtral-mini-local', 'voxtral-small-local'
              ]), 
              help='Transcription model: Whisper (whisper-*), OpenAI API (*-api), Voxtral API (voxtral-*-api), or Voxtral Local (*-local)')
@optgroup.option('--language', '-l', help='Language code (auto-detect if not specified)')
@optgroup.option('--transcription-prompt', help='A prompt to guide transcription (only works for OpenAI models)')
@optgroup.option('--start', help='Start time of the segment to transcribe (e.g., "00:01:30" or "1:30")')
@optgroup.option('--end', help='End time of the segment to transcribe (e.g., "00:02:30" or "2:30")')
@optgroup.option('--auto-download', is_flag=True, help='Automatically download local models without confirmation (use with caution for large models)')

# LLM Cleaning Options
@optgroup.group('LLM Cleaning Options')
@optgroup.option('--clean/--no-clean', 'clean_transcript', default=True, help='Clean transcript using LLM (default: clean)')
@optgroup.option('--llm-model', default='gemini-2.0-flash-exp', help='LLM model for cleaning (default: gemini-2.0-flash-exp). Run `llm models` for a list of supported models, and see https://github.com/simonw/llm for details.')
@optgroup.option('--cleaning-style', type=click.Choice(['presentation', 'conversation', 'lecture']), 
              default='presentation', help='Style of cleaning to apply (default: presentation)')

# Download/Authentication Options
@optgroup.group('Download/Authentication Options')
@optgroup.option('--cookies', help='Netscape formatted file to read cookies from and dump cookie jar in. See https://github.com/yt-dlp/yt-dlp/wiki/Extractors for details.')
@optgroup.option('--cookies-from-browser', help='The name of the browser to load cookies from. Currently supported browsers are: brave, chrome, chromium, edge, firefox, opera, safari, vivaldi, whale. Optionally, the KEYRING used for decrypting Chromium cookies on Linux, the name/path of the PROFILE to load cookies from, and the CONTAINER name (if Firefox) can be given with their respective separators. See https://github.com/yt-dlp/yt-dlp/wiki/Extractors for details.')
def transcribe(input_path, output, output_format, model, language, keep_audio, clean_transcript, llm_model, cleaning_style, save_raw, start, end, transcription_prompt, auto_download, cookies, cookies_from_browser):
    """
    Transcribe a YouTube video, local audio or video file to text.

    INPUT is the URL of a YouTube video or the path to a local audio/video file.
    Supported local audio formats are: MP3, WAV, M4A, OPUS.
    Supported local video formats are: MP4, MKV, MOV.
    
    \b
    Available models:
      • Whisper (local): whisper-tiny, whisper-base, whisper-small, whisper-medium, whisper-large, whisper-turbo 
      • OpenAI API: whisper-1-api, gpt-4o-transcribe-api, gpt-4o-mini-transcribe-api (requires OPENAI_API_KEY)
      • Voxtral API: voxtral-mini-api, voxtral-small-api (requires MISTRAL_API_KEY)
      • Voxtral Local: voxtral-mini-local, voxtral-small-local (requires transformers) 
    """
    try:
        is_local_file = os.path.exists(input_path)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            if is_local_file:
                if input_path.lower().endswith(('.mp3', '.wav', '.m4a', '.opus')):
                    click.echo(f"> Processing local audio file: {input_path}")
                    audio_path = input_path
                elif input_path.lower().endswith(('.mp4', '.mkv', '.mov')):
                    click.echo(f"> Processing local video file: {input_path}")
                    audio_path = extract_audio(input_path, temp_dir)
                else:
                    raise ValueError("Unsupported file type. Please provide a YouTube URL or a local audio/video file.")
                video_title = None
            else:
                click.echo(f"> Downloading audio from: {input_path}")
                audio_path, video_title = download_audio(input_path, temp_dir, start, end, cookies, cookies_from_browser)

            if is_local_file and (start or end):
                click.echo(f"> Trimming audio from {start or 'start'} to {end or 'end'}...")
                trimmed_audio_path = os.path.join(temp_dir, "trimmed_audio.mp3")
                trim_audio(audio_path, trimmed_audio_path, start, end)
                audio_path = trimmed_audio_path

            if output is None:
                if is_local_file:
                    base_name = os.path.splitext(os.path.basename(input_path))[0]
                else:
                    base_name = get_safe_filename(video_title)
                output = f"{base_name}.{output_format}"

            click.echo(f"> Transcribing with {model} model...")
            result = transcribe_audio(audio_path, model, language, transcription_prompt, auto_download)
            
            process_transcription(result, output, output_format, clean_transcript, llm_model, cleaning_style, save_raw, audio_path, is_local_file, keep_audio)

    except Exception as e:
        click.echo(f"> Error: {str(e)}", err=True)
        raise click.Abort()

def get_safe_filename(title, max_length=50):
    """Create a safe, shortened, snake_cased filename from a title."""
    if not title:
        return "transcription"
    # Remove special characters
    safe_title = "".join(c for c in title if c.isalnum() or c.isspace()).strip()
    # Replace spaces with underscores
    snake_cased = "_".join(safe_title.lower().split())
    # Truncate to max_length
    return snake_cased[:max_length]

def process_transcription(result, output, output_format, clean_transcript, llm_model, cleaning_style, save_raw, audio_path, is_local_file, keep_audio):
    """Helper function to process and save the transcription results."""
    try:
        output_path = Path(output)
        
        # Save raw transcript if requested
        if save_raw:
            raw_output_path = output_path.with_name(
                output_path.stem + '_raw' + output_path.suffix
            )
            raw_formatted = format_output(result, output_format)
            with open(raw_output_path, 'w', encoding='utf-8') as f:
                f.write(raw_formatted)
            click.echo(f"> Raw transcript saved to: {raw_output_path}")

        # Clean transcript if requested
        final_result = result
        if clean_transcript:
            click.echo(f"> Cleaning transcript with {llm_model}...")
            raw_text = result['text']
            cleaned_text = clean_long_transcript(raw_text, llm_model, cleaning_style)
            
            if cleaned_text:
                final_result = result.copy()
                final_result['text'] = cleaned_text
                if output_format in ['srt', 'vtt'] and 'segments' in result:
                    click.echo("> Note: Cleaned text with original timing segments")
            else:
                click.echo("> Cleaning failed, using original transcript")
        
        # Format and save final output
        final_output_path = output_path
        if not clean_transcript:
            # If not cleaning, the raw output is the final one
            raw_formatted = format_output(result, output_format)
            with open(final_output_path, 'w', encoding='utf-8') as f:
                f.write(raw_formatted)
        else:
            formatted_output = format_output(final_result, output_format)
            with open(final_output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_output)

        # Keep audio file if requested
        if keep_audio:
            final_audio_path = output_path.with_suffix('.mp3')
            if is_local_file:
                import shutil
                shutil.copy(audio_path, final_audio_path)
            else:
                if os.path.exists(audio_path):
                    os.rename(audio_path, final_audio_path)
            click.echo(f"> Audio saved to: {final_audio_path}")
        
        click.echo(f"> Transcription saved to: {final_output_path}")

    except Exception as e:
        click.echo(f"> Error in processing: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    transcribe()