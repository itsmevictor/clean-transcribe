#!/usr/bin/env python3
import click
import os
import tempfile
from pathlib import Path
from .downloader import download_audio
from .transcriber import transcribe_audio
from .formatter import format_output
from .cleaner import clean_long_transcript
from .trimmer import trim_audio

@click.command()
@click.argument('input_path', metavar='<URL or local path>')
@click.option('--output', '-o', default=None, help='Output file path. Default for YouTube videos is a shortened, snake-cased version of the video title. Default for local files is the input filename with a new extension.')
@click.option('--format', '-f', 'output_format', default='txt', 
              type=click.Choice(['txt', 'srt', 'vtt']), help='Output format (default: txt)')
@click.option('--model', '-m', default='small', 
              type=click.Choice(['tiny', 'base', 'small', 'medium', 'large', 'turbo']), 
              help='Whisper model size')
@click.option('--language', '-l', help='Language code (auto-detect if not specified)')
@click.option('--keep-audio', is_flag=True, help='Keep audio file (if downloaded)')
@click.option('--clean/--no-clean', 'clean_transcript', default=True, help='Clean transcript using LLM (default: clean)')
@click.option('--llm-model', default='gemini-2.0-flash-exp', help='LLM model for cleaning (default: gemini-2.0-flash-exp)')
@click.option('--cleaning-style', type=click.Choice(['presentation', 'conversation', 'lecture']), 
              default='presentation', help='Style of cleaning to apply (default: presentation)')
@click.option('--save-raw', is_flag=True, help='Also save raw transcript before cleaning')
@click.option('--start', help='Start time of the segment to transcribe (e.g., "00:01:30" or "1:30")')
@click.option('--end', help='End time of the segment to transcribe (e.g., "00:02:30" or "2:30")')
def transcribe(input_path, output, output_format, model, language, keep_audio, clean_transcript, llm_model, cleaning_style, save_raw, start, end):
    """
    Transcribe a YouTube video or a local audio file to text.

    INPUT is the URL of a YouTube video or the path to a local audio file.
    Supported local audio formats are: MP3, WAV, M4A.
    """
    try:
        is_local_file = os.path.exists(input_path)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            if is_local_file:
                click.echo(f"🎧 Processing local audio file: {input_path}")
                if not input_path.lower().endswith(('.mp3', '.wav', '.m4a')):
                    raise ValueError("Only MP3, WAV, or M4A files are supported for local input.")
                audio_path = input_path
                video_title = None
            else:
                click.echo(f"🎥 Downloading audio from: {input_path}")
                audio_path, video_title = download_audio(input_path, temp_dir, start, end)

            if is_local_file and (start or end):
                click.echo(f"✂️  Trimming audio from {start or 'start'} to {end or 'end'}...")
                trimmed_audio_path = os.path.join(temp_dir, "trimmed_audio.mp3")
                trim_audio(audio_path, trimmed_audio_path, start, end)
                audio_path = trimmed_audio_path

            if output is None:
                if is_local_file:
                    base_name = os.path.splitext(os.path.basename(input_path))[0]
                else:
                    base_name = get_safe_filename(video_title)
                output = f"{base_name}.{output_format}"

            click.echo(f"🎙️  Transcribing with {model} model...")
            result = transcribe_audio(audio_path, model, language)
            
            process_transcription(result, output, output_format, clean_transcript, llm_model, cleaning_style, save_raw, audio_path, is_local_file, keep_audio)

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
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
            click.echo(f"📄 Raw transcript saved to: {raw_output_path}")

        # Clean transcript if requested
        final_result = result
        if clean_transcript:
            click.echo(f"🧹 Cleaning transcript with {llm_model}...")
            raw_text = result['text']
            cleaned_text = clean_long_transcript(raw_text, llm_model, cleaning_style)
            
            if cleaned_text:
                final_result = result.copy()
                final_result['text'] = cleaned_text
                if output_format in ['srt', 'vtt'] and 'segments' in result:
                    click.echo("ℹ️  Note: Cleaned text with original timing segments")
            else:
                click.echo("⚠️  Cleaning failed, using original transcript")
        
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
            click.echo(f"📁 Audio saved to: {final_audio_path}")
        
        click.echo(f"✅ Transcription saved to: {final_output_path}")

    except Exception as e:
        click.echo(f"�� Error in processing: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    transcribe()