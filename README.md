# Clean Transcriber

A command-line tool to turn any YouTube video, local audio or video file into a clean, readable text transcript. It uses the transcription model of your choice (local or API-based) for transcription and your preferred LLM to automatically clean and reformat the output.

## Features

1. **Multiple input formats**: Supports various audio and video formats for flexible usage (e.g., YouTube URL, `.mp3`, `.wav`, `.m4a`, `.opus`, `.mp4`, `.mkv`, `.mov`).
2. **Multiple output format**: Generate clean transcripts in TXT, SRT, or VTT formats.
3. **Flexible transcription models**: Choose from various local (Whisper, Voxtral) and API-based (OpenAI, Mistral) models for different use cases.
5. **LLM-powered cleaning** that removes filler words, fixes grammar, and organizes content into readable paragraphs.   
6. **Wide LLM support** - use Gemini, ChatGPT, Claude or any other (local) LLM for cleaning.

## Quick Start

```bash
# Transcribe a YouTube video
clean-transcribe "https://www.youtube.com/watch?v=VIDEO_ID"

# Transcribe a local video file
clean-transcribe "/path/to/your/video.mp4"

# Transcribe a specific segment of a video
clean-transcribe "https://www.youtube.com/watch?v=VIDEO_ID" --start "1:30" --end "2:30"

# Create clean subtitles from a video
clean-transcribe "https://www.youtube.com/watch?v=VIDEO_ID" -f srt -o subtitles.srt
```

## Installation

**Option 1: Clone and run**
```bash
git clone https://github.com/itsmevictor/clean-transcribe
cd clean-transcribe
pip install -r requirements.txt
clean-transcribe "path/to/your/audio.mp3"
```

**Option 2: Install as package**
```bash
git clone https://github.com/itsmevictor/clean-transcribe
cd clean-transcribe
pip install -e .
clean-transcribe "https://www.youtube.com/watch?v=dQw4w9WgXcQ"   
```

## Usage Examples

**Transcribe a YouTube video:**
```bash
clean-transcribe "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Transcribe a local audio file:**
```bash
clean-transcribe "path/to/your/audio.mp3" -o "transcript.txt"
```

**Transcribe a specific segment:**
```bash
clean-transcribe "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --start "00:01:30" --end "00:02:30"
```

**Create clean subtitles from a video:**
```bash
clean-transcribe "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -f srt
```

**High-quality lecture transcription from a local file:**
```bash
clean-transcribe "lecture.wav" \
    -m whisper-large \
    --llm-model gemini-2.0-flash-exp \
    --cleaning-style lecture \
    --save-raw
```

## Configuration

### Key Options
- `--format, -f`: Output format (txt, srt, vtt)
- `--model, -m`: Transcription model (whisper-tiny, whisper-base, whisper-small, whisper-medium, whisper-large, whisper-turbo, whisper-1-api, gpt-4o-transcribe-api, gpt-4o-mini-transcribe-api, voxtral-mini-api, voxtral-small-api, voxtral-mini-local, voxtral-small-local)
- `--start`: Start time for transcription (e.g., "1:30")
- `--end`: End time for transcription (e.g., "2:30")
- `--transcription-prompt`: Custom prompt for Whisper to guide transcription
- `--llm-model`: LLM for cleaning (gemini-2.0-flash-exp, gpt-4o-mini, etc.)
- `--cleaning-style`: presentation, conversation, or lecture
- `--save-raw`: Keep both raw and cleaned versions
- `--no-clean`: Skip AI cleaning

## LLM-Powered Cleaning Setup

### Quick Setup (Recommended)
```bash
# Install and configure Gemini (fast + cost-effective)
llm install llm-gemini
llm keys set gemini
# Enter your Gemini API key when prompted

# Or use any other LLM provider

# OpenAI
llm keys set openai

# Anthropic Claude  
llm install llm-claude-3
llm keys set claude
```

*Uses Simon Willison's excellent [llm package](https://github.com/simonw/llm) for provider flexibility.*

### Cleaning Process

**What it does:**
- Removes filler words (um, uh, so, like, you know, etc.)
- Fixes grammar and punctuation errors  
- Organizes content into logical paragraphs
- Maintains original meaning and context

**Cleaning styles:**
- **presentation**: Professional tone, organized paragraphs
- **conversation**: Natural flow, minimal cleanup
- **lecture**: Educational format, clear sections for notes

*Note: SRT/VTT preserve timing while cleaning text content.*

## Feedback

I'd love to hear your feedback! If you encounter any issues, have suggestions for new features, or just want to share your experience, please don't hesitate to [open an issue](https://github.com/itsmevictor/clean-transcribe/issues).
