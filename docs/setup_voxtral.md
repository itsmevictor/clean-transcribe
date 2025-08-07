# Voxtral Local Models Setup Guide

## Quick Fix for the Error

The error you encountered is due to missing dependencies. Here's how to fix it:

```bash
# Install required dependencies for Voxtral local models
pip install torch transformers>=4.54.0 accelerate safetensors mistral-common>=1.8.1 packaging

# Alternative: Install with audio support
pip install "mistral-common[audio]>=1.8.1"
```

## Test the Installation

After installing the dependencies, test with:

```bash
python -c "
import mistral_common
import transformers
print('mistral-common version:', mistral_common.__version__)
print('transformers version:', transformers.__version__)
print('Dependencies installed successfully!')
"
```

## Model Information

- **voxtral-mini-local**: `mistralai/Voxtral-Mini-3B-2507` (~6GB)
- **voxtral-small-local**: `mistralai/Voxtral-Small-24B-2507` (~48GB)

Both models are publicly available and don't require special access.

## Usage After Setup

```bash
# Test with the mini model first (smaller download)
clean-transcribe "https://www.youtube.com/watch?v=s18eJD1fLko" --model voxtral-mini-local

# For better quality, use the small model (requires more resources)
clean-transcribe "https://www.youtube.com/watch?v=s18eJD1fLko" --model voxtral-small-local
```

## Hardware Requirements

- **voxtral-mini-local**: ~9.5GB GPU RAM (recommended) or CPU with sufficient RAM
- **voxtral-small-local**: ~55GB GPU RAM (recommended) or very high CPU RAM

## Troubleshooting

1. **"mistral-common not found"**: Install with `pip install mistral-common>=1.8.1`
2. **"transformers version too old"**: Upgrade with `pip install transformers>=4.54.0`
3. **CUDA out of memory**: Try CPU inference or use the mini model instead
4. **Model download fails**: Check internet connection and disk space

## Alternative: Use Voxtral API

If local models are too resource-intensive, use the API instead:

```bash
export MISTRAL_API_KEY="your_api_key"
clean-transcribe "https://www.youtube.com/watch?v=s18eJD1fLko" --model voxtral-mini-latest
```