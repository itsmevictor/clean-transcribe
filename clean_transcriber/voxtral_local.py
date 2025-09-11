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
        missing_deps.append("mistral-common[audio]>=1.8.1")
    
    # Check additional dependencies that Voxtral models might need
    try:
        import timm
    except ImportError:
        missing_deps.append("timm")
    
    try:
        import accelerate
    except ImportError:
        missing_deps.append("accelerate")
    
    try:
        import safetensors
    except ImportError:
        missing_deps.append("safetensors")
    
    try:
        import librosa
    except ImportError:
        missing_deps.append("librosa")
    
    if missing_deps:
        deps_str = " ".join(missing_deps)
        raise ImportError(
            f"> Local Voxtral models require missing dependencies: {', '.join(missing_deps)}\n\n"
            "> Quick fix:\n"
            f"pip install {deps_str}\n\n"
            "> For more details, see setup_voxtral.md\n"
            "> Note: You may need to restart your runtime after installation."
        )
    
    # Now import after dependency check
    from transformers import VoxtralForConditionalGeneration, AutoProcessor
    
    # Map model names to HuggingFace model IDs
    model_mapping = {
        'voxtral-mini-local': 'mistralai/Voxtral-Mini-3B-2507',
        'voxtral-small-local': 'mistralai/Voxtral-Small-24B-2507'
    }
    
    if model_name not in model_mapping:
        raise ValueError(f"Unknown local Voxtral model: {model_name}")
    
    hf_model_id = model_mapping[model_name]
    
    # Check if model is already cached locally
    from transformers.utils import is_offline_mode
    
    model_size_gb = 48 if 'small' in model_name.lower() else 6  # 48GB for small, 6GB for mini
    
    # Check if model exists in cache by checking HuggingFace cache directory
    model_is_cached = False
    try:
        from huggingface_hub import try_to_load_from_cache
        from pathlib import Path
        import os
        
        # Check if key model files exist in cache
        cache_dir = Path.home() / '.cache' / 'huggingface' / 'hub'
        model_cache_dir = cache_dir / f"models--{hf_model_id.replace('/', '--')}"
        
        if model_cache_dir.exists():
            # Look for model files that indicate successful download
            for file_pattern in ['*.safetensors', '*.bin', 'config.json']:
                if any(model_cache_dir.rglob(file_pattern)):
                    model_is_cached = True
                    break
    except Exception as e:
        # Fall back to False if any error occurs
        model_is_cached = False
    
    if not auto_download and not model_is_cached:
        click.echo(f"> Warning: {model_name} is approximately {model_size_gb}GB")
        click.echo("This will require significant disk space and memory.")
        if not click.confirm("Do you want to continue?"):
            raise click.Abort()
    elif model_is_cached:
        click.echo(f"> Using cached {model_name} model ({model_size_gb}GB)")
    
    # Determine device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    
    click.echo(f"> Using device: {device}")
    
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
                model = VoxtralForConditionalGeneration.from_pretrained(
                    hf_model_id,
                    torch_dtype=torch_dtype,
                    device_map=device if device == "cuda" else None,
                )
                bar.update(1)
            except Exception as e:
                error_str = str(e).lower()
                if "mistral-common" in error_str:
                    raise Exception("Missing mistral-common library. Install with: pip install 'mistral-common[audio]>=1.8.1'")
                elif "timm" in error_str or "imagenetinfo" in error_str:
                    raise Exception(
                        "Voxtral model dependency issue with 'timm' library.\n"
                        "Try updating timm: pip install --upgrade timm\n"
                        "If that doesn't work, try: pip install timm==0.9.12"
                    )
                elif "configuration" in error_str and "voxtral" in error_str:
                    raise Exception(
                        "Voxtral model configuration issue. This might be due to:\n"
                        "1. Incompatible transformers version\n"
                        "2. Missing model files\n" 
                        "Try: pip install --upgrade transformers>=4.54.0"
                    )
                else:
                    raise e
            
            # Move model to device if using CPU
            if device == "cpu":
                model = model.to(device)
            bar.update(1)
    
    except Exception as e:
        click.echo(f"> Failed to load Voxtral model: {str(e)}")
        raise e
    
    # Prepare transcription options
    if language:
        # Note: Voxtral models may not support language specification the same way as Whisper
        click.echo(f"> Language specification ({language}) may not be supported by Voxtral models")
    
    if transcription_prompt:
        # Note: Voxtral models do not support prompts the same way as Whisper
        click.echo(f"> Transcription prompts are not supported by Voxtral models")

    # Transcribe audio using Voxtral
    try:
        with click.progressbar(length=1, label='Transcribing with Voxtral') as bar:
            # Use the correct transcription request format from the README
            inputs = processor.apply_transcription_request(
                language=language or "en",
                audio=audio_path,
                model_id=hf_model_id
            )
            
            # Move inputs to device and set dtype
            if device == "cuda":
                inputs = inputs.to(device, dtype=torch_dtype)
            else:
                inputs = inputs.to(device)
            
            # Generate transcription (following HuggingFace docs exactly)
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=500
                )
            
            # Decode the transcription (only the new tokens)
            decoded_outputs = processor.batch_decode(
                outputs[:, inputs.input_ids.shape[1]:], 
                skip_special_tokens=True
            )
            transcription = decoded_outputs[0]
            bar.update(1)
            
    except Exception as e:
        raise Exception(f"Transcription failed: {e}")
    
    # Convert to Whisper-compatible format
    whisper_format = _convert_voxtral_to_whisper_format(transcription)
    
    return whisper_format


def _convert_voxtral_to_whisper_format(transcription: str) -> Dict[str, Any]:
    """Convert Voxtral transcription text to Whisper-compatible format."""
    
    # For now, create a single segment with the entire transcription
    # TODO: Could potentially split into segments based on punctuation/sentences
    segments = [{
        'id': 0,
        'seek': 0,
        'start': 0.0,
        'end': 0.0,  # We don't have timing information from basic Voxtral usage
        'text': transcription,
        'tokens': [],
        'temperature': 0.0,
        'avg_logprob': 0.0,
        'compression_ratio': 1.0,
        'no_speech_prob': 0.0
    }]
    
    return {
        'text': transcription,
        'segments': segments,
        'language': 'unknown'  # Voxtral may not provide language detection
    }


def _convert_to_whisper_format(voxtral_result: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Voxtral pipeline result to Whisper-compatible format (legacy function)."""
    
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