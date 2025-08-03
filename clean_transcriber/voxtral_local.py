import os
import warnings
import click
from typing import Optional, Dict, Any
from pathlib import Path

def transcribe_audio_voxtral_local(audio_path: str, model_name: str = 'voxtral-mini-local', 
                                  language: Optional[str] = None, transcription_prompt: Optional[str] = None,
                                  auto_download: bool = False) -> Dict[str, Any]:
    """Transcribe audio using local Voxtral models."""
    
    # Check dependencies
    missing_deps = []
    try:
        import torch
    except ImportError:
        missing_deps.append("torch>=2.0.0")
    
    try:
        import transformers
        # Check transformers version
        from packaging import version
        if version.parse(transformers.__version__) < version.parse("4.54.0"):
            missing_deps.append(f"transformers>=4.54.0 (current: {transformers.__version__})")
    except ImportError:
        missing_deps.append("transformers>=4.54.0")
    
    try:
        import mistral_common
    except ImportError:
        missing_deps.append("mistral-common>=1.8.1")
    
    if missing_deps:
        deps_str = " ".join(missing_deps)
        raise ImportError(
            f"❌ Local Voxtral models require missing dependencies: {', '.join(missing_deps)}\n\n"
            "🔧 Quick fix:\n"
            f"pip install {deps_str}\n\n"
            "📖 For more details, see setup_voxtral.md\n"
            "⚠️  Note: You may need to restart your runtime after installation."
        )
    
    # Now import after dependency check
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    
    # Map model names to HuggingFace model IDs
    model_mapping = {
        'voxtral-mini-local': 'mistralai/Voxtral-Mini-3B-2507',
        'voxtral-small-local': 'mistralai/Voxtral-Small-24B-2507'
    }
    
    if model_name not in model_mapping:
        raise ValueError(f"Unknown local Voxtral model: {model_name}")
    
    hf_model_id = model_mapping[model_name]
    
    # Warn about large model sizes
    if 'small' in model_name.lower():
        model_size_gb = 48  # Approximate size for 24B model
        if not auto_download:
            click.echo(f"⚠️  Warning: {model_name} is approximately {model_size_gb}GB")
            click.echo("This will require significant disk space and memory.")
            if not click.confirm("Do you want to continue?"):
                raise click.Abort()
    
    # Determine device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    
    click.echo(f"🔧 Using device: {device}")
    
    try:
        # Load model and processor
        with click.progressbar(length=3, label='Loading Voxtral model') as bar:
            click.echo(f"Loading processor for {hf_model_id}...")
            # Load processor
            try:
                processor = AutoProcessor.from_pretrained(hf_model_id)
                bar.update(1)
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    raise Exception(f"Access denied to model {hf_model_id}. You may need to:\n"
                                  "1. Log in to HuggingFace: huggingface-cli login\n"
                                  "2. Request access to the model on HuggingFace Hub")
                elif "404" in str(e) or "not found" in str(e).lower():
                    raise Exception(f"Model {hf_model_id} not found on HuggingFace Hub")
                else:
                    raise e
            
            click.echo(f"Loading model {hf_model_id} ({model_size_gb if 'small' in model_name.lower() else 6}GB)...")
            # Load model
            try:
                model = AutoModelForSpeechSeq2Seq.from_pretrained(
                    hf_model_id,
                    torch_dtype=torch_dtype,
                    device_map="auto" if device == "cuda" else None,
                    use_safetensors=True
                )
                bar.update(1)
            except Exception as e:
                if "mistral-common" in str(e).lower():
                    raise Exception("Missing mistral-common library. Install with: pip install mistral-common>=1.8.1")
                else:
                    raise e
            
            # Create pipeline
            pipe = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor,
                torch_dtype=torch_dtype,
                device_map="auto" if device == "cuda" else None,
            )
            bar.update(1)
    
    except Exception as e:
        click.echo(f"❌ Failed to load Voxtral model: {str(e)}")
        raise e
    
    # Prepare transcription options
    generate_kwargs = {}
    if language:
        # Note: Voxtral models may not support language specification the same way as Whisper
        click.echo(f"⚠️  Language specification ({language}) may not be supported by Voxtral models")
    
    if transcription_prompt:
        # Note: Voxtral models may not support prompts the same way as Whisper
        click.echo(f"⚠️  Transcription prompts may not be supported by Voxtral models")
    
    # Transcribe audio
    try:
        with click.progressbar(length=1, label='Transcribing with Voxtral') as bar:
            result = pipe(audio_path, generate_kwargs=generate_kwargs, return_timestamps=True)
            bar.update(1)
    except Exception as e:
        raise Exception(f"Transcription failed: {e}")
    
    # Convert to Whisper-compatible format
    whisper_format = _convert_to_whisper_format(result)
    
    return whisper_format


def _convert_to_whisper_format(voxtral_result: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Voxtral pipeline result to Whisper-compatible format."""
    
    # Extract main text
    text = voxtral_result.get('text', '')
    
    # Convert chunks/segments if available
    segments = []
    if 'chunks' in voxtral_result:
        for i, chunk in enumerate(voxtral_result['chunks']):
            # Convert to Whisper segment format
            whisper_segment = {
                'id': i,
                'seek': 0,
                'start': chunk.get('timestamp', [0, 0])[0] if chunk.get('timestamp') else 0.0,
                'end': chunk.get('timestamp', [0, 0])[1] if chunk.get('timestamp') else 0.0,
                'text': chunk.get('text', ''),
                'tokens': [],
                'temperature': 0.0,
                'avg_logprob': 0.0,
                'compression_ratio': 1.0,
                'no_speech_prob': 0.0
            }
            segments.append(whisper_segment)
    
    return {
        'text': text,
        'segments': segments,
        'language': 'unknown'  # Voxtral may not provide language detection
    }


def is_voxtral_local_model(model_name: str) -> bool:
    """Check if the model name corresponds to a local Voxtral model."""
    voxtral_local_models = [
        'voxtral-mini-local',
        'voxtral-small-local'
    ]
    return model_name in voxtral_local_models


def check_voxtral_local_setup() -> bool:
    """Check if local Voxtral dependencies are available."""
    try:
        import torch
        import transformers
        return True
    except ImportError:
        return False


def get_model_info(model_name: str) -> Dict[str, Any]:
    """Get information about a local Voxtral model."""
    model_info = {
        'voxtral-mini-local': {
            'hf_id': 'mistralai/Voxtral-Mini-3B-2507',
            'size_gb': 6,
            'params': '3B',
            'description': 'Smaller, faster model suitable for most use cases'
        },
        'voxtral-small-local': {
            'hf_id': 'mistralai/Voxtral-Small-24B-2507',
            'size_gb': 48,
            'params': '24B',
            'description': 'Larger, more accurate model requiring significant resources'
        }
    }
    return model_info.get(model_name, {})