import subprocess
import sys
import click
from typing import Optional

def clean_transcript(text: str, model: str = "gemini-2.0-flash-exp", style: str = "presentation") -> Optional[str]:
    """Clean transcript using LLM via the llm package."""
    
    # Choose cleaning prompt based on style
    prompts = {
        "presentation": """Please clean up this transcript from a presentation/speech. Your task:

1. Remove filler words (um, uh, so, like, you know, etc.)
2. Fix grammar and punctuation
3. Organize into clear paragraphs based on topic changes
4. Maintain the original meaning and tone
5. Keep it natural and readable
6. Preserve important emphasis or repetition if meaningful

Do that while keeping as close to the original text as possible. 
Do NOT translate the text. Keep the original language intact.
Return only the cleaned transcript, no explanations or comments.

Transcript to clean:
""",
        "conversation": """Please clean up this transcript from a conversation. Your task:

1. Remove filler words and false starts
2. Fix grammar while keeping conversational tone
3. Organize into paragraphs by speaker or topic
4. Maintain natural flow and personality
5. Preserve important pauses or emphasis
6. Keep it readable but authentic

Do that while keeping as close to the original text as possible. 
Do NOT translate the text. Keep the original language intact.
Return only the cleaned transcript, no explanations or comments.

Transcript to clean:
""",
        "lecture": """Please clean up this transcript from a lecture or educational content. Your task:

1. Remove filler words and repetitive phrases
2. Fix grammar and punctuation
3. Organize into clear sections and paragraphs
4. Maintain academic tone and clarity
5. Preserve key points and emphasis
6. Make it suitable for study notes

Do that while keeping as close to the original text as possible. 
Do NOT translate the text. Keep the original language intact.
Return only the cleaned transcript, no explanations or comments.

Transcript to clean:
"""
    }
    
    prompt = prompts.get(style, prompts["presentation"]) + text
    
    try:
        # Check if llm is available
        result = subprocess.run(['llm', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            click.echo("> LLM package not found. Install with: pip install llm", err=True)
            return None
        
        # Run llm command
        cmd = ['llm', '-m', model, prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            cleaned_text = result.stdout.strip()
            if cleaned_text:
                return cleaned_text
            else:
                click.echo("> LLM returned empty response", err=True)
                return None
        else:
            error_msg = result.stderr.strip()
            if "No API key" in error_msg or "authentication" in error_msg.lower():
                click.echo("> LLM API key not configured. Run: llm keys set gemini", err=True)
            elif "Model not found" in error_msg:
                click.echo(f"> Model '{model}' not available. Try: gemini-1.5-pro or gpt-4o-mini", err=True)
            else:
                click.echo(f"> LLM error: {error_msg}", err=True)
            return None
            
    except subprocess.TimeoutExpired:
        click.echo("> LLM request timed out", err=True)
        return None
    except FileNotFoundError:
        click.echo("> LLM package not found. Install with: pip install llm", err=True)
        return None
    except Exception as e:
        click.echo(f"> Unexpected error during cleaning: {str(e)}", err=True)
        return None

def chunk_text(text: str, max_chunk_size: int = 20000) -> list[str]:
    """Split text into chunks for processing by LLM."""
    if len(text) <= max_chunk_size:
        return [text]
    
    # Try to split on sentence boundaries
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence += '. '  # Re-add the period
        if len(current_chunk + sentence) <= max_chunk_size:
            current_chunk += sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def clean_long_transcript(text: str, model: str = "gemini-2.0-flash-exp", style: str = "presentation") -> Optional[str]:
    """Clean very long transcripts by processing in chunks."""
    
    # Check if text needs chunking
    if len(text) <= 20000:
        return clean_transcript(text, model, style)
    
    click.echo("> Processing long transcript in chunks...")
    
    chunks = chunk_text(text)
    cleaned_chunks = []
    
    with click.progressbar(chunks, label='Cleaning transcript') as chunk_bar:
        for chunk in chunk_bar:
            cleaned_chunk = clean_transcript(chunk, model, style)
            if cleaned_chunk:
                cleaned_chunks.append(cleaned_chunk)
            else:
                # If cleaning fails, use original chunk
                cleaned_chunks.append(chunk)
    
    return "\n\n".join(cleaned_chunks)

def get_available_models() -> list[str]:
    """Get list of available LLM models."""
    try:
        result = subprocess.run(['llm', 'models'], capture_output=True, text=True)
        if result.returncode == 0:
            # Parse model names from output
            models = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Provider:'):
                    model_name = line.strip().split()[0]
                    if model_name:
                        models.append(model_name)
            return models
        return []
    except:
        return []
