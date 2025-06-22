#!/usr/bin/env python3
import click
import os
import tempfile
from pathlib import Path
from .downloader import download_audio
from .transcriber import transcribe_audio
from .formatter import format_output
from .cleaner import clean_long_transcript

@click.command()
@click.argument('url')
@click.option('--output', '-o', default='transcript.txt', help='Output file path')
@click.option('--format', '-f', 'output_format', default='txt', 
              type=click.Choice(['txt', 'srt', 'vtt']), help='Output format (default: txt)')
@click.option('--model', '-m', default='turbo', 
              type=click.Choice(['tiny', 'base', 'small', 'medium', 'large', 'turbo']), 
              help='Whisper model size')
@click.option('--language', '-l', help='Language code (auto-detect if not specified)')
@click.option('--keep-audio', is_flag=True, help='Keep downloaded audio file')
@click.option('--clean/--no-clean', default=True, help='Clean transcript using LLM (default: clean)')
@click.option('--llm-model', default='gemini-2.0-flash-exp', help='LLM model for cleaning (default: gemini-2.0-flash-exp)')
@click.option('--cleaning-style', type=click.Choice(['presentation', 'conversation', 'lecture']), 
              default='presentation', help='Style of cleaning to apply (default: presentation)')
@click.option('--save-raw', is_flag=True, help='Also save raw transcript before cleaning')
def transcribe(url, output, output_format, model, language, keep_audio, clean, llm_model, cleaning_style, save_raw):
    """Transcribe YouTube video to text using OpenAI Whisper."""
    try:
        click.echo(f"🎥 Downloading audio from: {url}")
        
        # Download audio to temporary file
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = download_audio(url, temp_dir)
            
            click.echo(f"🎙️  Transcribing with {model} model...")
            
            # Transcribe audio
            result = transcribe_audio(audio_path, model, language)
            
            # Save raw transcript if requested
            if save_raw or clean:
                raw_output_path = Path(output)
                if clean:
                    # Modify filename to indicate raw version
                    raw_output_path = raw_output_path.with_name(
                        raw_output_path.stem + '_raw' + raw_output_path.suffix
                    )
                
                if save_raw or not clean:
                    raw_formatted = format_output(result, output_format)
                    with open(raw_output_path, 'w', encoding='utf-8') as f:
                        f.write(raw_formatted)
                    
                    if save_raw:
                        click.echo(f"📄 Raw transcript saved to: {raw_output_path}")
            
            # Clean transcript if requested
            final_result = result
            if clean:
                click.echo(f"🧹 Cleaning transcript with {llm_model}...")
                raw_text = result['text']
                cleaned_text = clean_long_transcript(raw_text, llm_model, cleaning_style)
                
                if cleaned_text:
                    # Create new result with cleaned text but preserve segments structure
                    final_result = result.copy()
                    final_result['text'] = cleaned_text
                    
                    # For SRT/VTT, we need to preserve timing but use cleaned text
                    if output_format in ['srt', 'vtt'] and 'segments' in result:
                        # Simple approach: distribute cleaned text across segments
                        # More sophisticated approach would require sentence alignment
                        click.echo("ℹ️  Note: Cleaned text with original timing segments")
                else:
                    click.echo("⚠️  Cleaning failed, using original transcript")
            
            # Format and save final output
            formatted_output = format_output(final_result, output_format)
            
            output_path = Path(output)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_output)
            
            # Keep audio file if requested
            if keep_audio:
                final_audio_path = output_path.with_suffix('.mp3')
                os.rename(audio_path, final_audio_path)
                click.echo(f"📁 Audio saved to: {final_audio_path}")
            
            click.echo(f"✅ Transcription saved to: {output_path}")
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    transcribe()