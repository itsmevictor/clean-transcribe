# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Clean Transcriber is a CLI tool that transcribes YouTube videos and local audio/video files using multiple transcription providers (Whisper, Voxtral API, Voxtral Local), then optionally cleans the transcripts using LLMs. The tool produces clean, readable text in multiple formats (TXT, SRT, VTT).

## Installation and Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install as editable package for development
pip install -e .

# Set up LLM for cleaning (recommended)
llm install llm-gemini
llm keys set gemini

# Set up Voxtral API (optional)
export MISTRAL_API_KEY="your_mistral_api_key"

# Set up Voxtral Local (optional, for local models)
pip install torch transformers>=4.54.0 accelerate safetensors mistral-common>=1.8.1 packaging
```

## Core Commands

```bash
# Basic transcription
clean-transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
clean-transcribe "/path/to/local/file.mp4"

# Test the CLI after changes
clean-transcribe --help

# Run a quick test with a short video segment
clean-transcribe "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --start "0:10" --end "0:30" --no-clean

# Test Voxtral models
clean-transcribe "/path/to/audio.mp3" --model voxtral-mini-latest  # API
clean-transcribe "/path/to/audio.mp3" --model voxtral-mini-local   # Local
```

## Architecture

The codebase follows a modular pipeline architecture with separate modules for each stage:

### Core Modules (`clean_transcriber/`)

- **`main.py`**: CLI interface using Click with option groups. Entry point at `clean_transcriber.main:transcribe`
- **`downloader.py`**: YouTube audio download using yt-dlp with cookie support
- **`extractor.py`**: Local video-to-audio extraction using FFmpeg
- **`transcriber.py`**: Multi-provider transcription routing (Whisper, Voxtral API, Voxtral Local)
- **`voxtral_api.py`**: Mistral API integration for Voxtral models
- **`voxtral_local.py`**: Local Voxtral model inference with HuggingFace
- **`cleaner.py`**: LLM-powered text cleaning via Simon Willison's `llm` package
- **`formatter.py`**: Output formatting for TXT/SRT/VTT formats
- **`trimmer.py`**: Audio segment trimming for time-based extraction

### Processing Pipeline

1. **Input Processing**: URL → audio download OR local file → audio extraction
2. **Audio Processing**: Optional trimming based on start/end times
3. **Transcription**: Multi-provider transcription (Whisper, Voxtral API, Voxtral Local) with language/prompt options
4. **Cleaning**: Optional LLM cleaning with style options (presentation/conversation/lecture)
5. **Output**: Format as TXT/SRT/VTT and save to specified location

### Key Dependencies

- **`whisper`**: Core transcription engine (built-in)
- **`requests`**: HTTP client for Voxtral API calls
- **`transformers`**: HuggingFace models for local Voxtral inference (optional)
- **`yt-dlp`**: YouTube download with cookie authentication
- **`llm`**: LLM provider abstraction for cleaning
- **`click`**: CLI framework with option groups
- **`ffmpeg-python`/`pydub`**: Audio processing

## Development Notes

- Entry point is defined in `setup.py` as `clean-transcribe=clean_transcriber.main:transcribe`
- No test suite currently exists - test manually with short video segments
- The tool handles both YouTube URLs and local audio/video files seamlessly
- LLM cleaning is optional but recommended for readability
- Supports time-based segment extraction for both YouTube and local files
- Cookie support enables access to restricted YouTube content

## Transcription Providers

### Whisper (Built-in)
- Models: `tiny`, `base`, `small`, `medium`, `large`, `turbo`
- Local inference, no API key required
- Supports language detection and prompts

### Voxtral API
- Models: `voxtral-mini-latest`, `voxtral-small-latest`
- Requires `MISTRAL_API_KEY` environment variable
- 15-minute max audio length per request
- Automatic base64 encoding for API upload

### Voxtral Local
- Models: `voxtral-mini-local` (~6GB), `voxtral-small-local` (~48GB)
- Requires `transformers`, `torch`, `accelerate` packages
- Downloads models from HuggingFace on first use
- GPU acceleration when available
- Size warnings for large models