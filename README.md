# Clean Transcriber

A command-line tool to turn any YouTube video, local audio or video file into a clean, readable text transcript. It uses OpenAI's Whisper for transcription and the LLM of your choice to automatically clean and reformat the output.

## Features

1. **YouTube & Local File Support**: Transcribe from a YouTube URL or a local audio/video file (`.mp3`, `.wav`, `.m4a`, `.mp4`, `.mkv`, `.mov`).
2. **Segment Selection**: Transcribe only a specific segment of the audio using `--start` and `--end` times.
3. **Fast and accurate transcription** using OpenAI's Whisper models
4. **LLM-powered cleaning** that removes filler words, fixes grammar, and organizes content into readable paragraphs
5. **Multiple output formats** (TXT, SRT, VTT) for any use case
6. **Flexible LLM support** - use Gemini, ChatGPT, Claude or any other (local) LLM for cleaning

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

**Requirements:**
- Python 3.7+
- FFmpeg (for audio processing)
- LLM API key (for cleaning, optional but recommended)

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
    -m large \
    --llm-model gemini-2.0-flash-exp \
    --cleaning-style lecture \
    --save-raw
```

**Raw transcript (no cleaning):**
```bash
clean-transcribe "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --no-clean
```

## Configuration

### Key Options
- `--format, -f`: Output format (txt, srt, vtt)
- `--model, -m`: Whisper model (tiny, base, small, medium, large, turbo)
- `--start`: Start time for transcription (e.g., "1:30")
- `--transcription-prompt`: Custom prompt for Whisper to guide transcription
- `--end`: End time for transcription (e.g., "2:30")
- `--llm-model`: LLM for cleaning (gemini-2.0-flash-exp, gpt-4o-mini, etc.)
- `--cleaning-style`: presentation, conversation, or lecture
- `--save-raw`: Keep both raw and cleaned versions
- `--no-clean`: Skip AI cleaning

<!-- ### Whisper Models
| Model | Speed | Accuracy | Size | Notes |
|-------|-------|----------|------|-------|
| tiny | Fastest | Basic | ~39 MB | Quick transcripts |
| base | Fast | Good | ~74 MB | Balanced option |
| small | Moderate | Good | ~244 MB | Good for most use cases |
| large | Slow | Best | ~1550 MB | Highest quality | -->

## LLM-Powered Cleaning Setup

### Quick Setup (Recommended)
```bash
# Install and configure Gemini (fast + cost-effective)
llm install llm-gemini
llm keys set gemini
# Enter your Gemini API key when prompted
```

### Alternative Providers
```bash
# OpenAI
llm keys set openai

# Anthropic Claude  
llm install llm-claude-3
llm keys set claude
```

**Popular models:**
- `gemini-2.0-flash-exp` (recommended - fast, cheap)
- `gpt-4o-mini` (OpenAI, fast)  
- `claude-3-5-sonnet-20241022` (Anthropic, high quality)

*Uses Simon Willison's excellent [llm package](https://github.com/simonw/llm) for provider flexibility.*

## How LLM Cleaning Works

**What it does:**
- Removes filler words (um, uh, so, like, you know, etc.)
- Fixes grammar and punctuation errors  
- Organizes content into logical paragraphs
- Maintains original meaning and context

**Cleaning styles:**
- **presentation**: Professional tone, organized paragraphs
- **conversation**: Natural flow, minimal cleanup
- **lecture**: Educational format, clear sections for notes

## Output Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| **TXT** | Plain text | Articles, notes, analysis |
| **SRT** | SubRip subtitles | Video editing, accessibility |
| **VTT** | WebVTT subtitles | Web players, streaming |

*Note: SRT/VTT preserve timing while cleaning text content.*

## Feedback

I'd love to hear your feedback! If you encounter any issues, have suggestions for new features, or just want to share your experience, please don't hesitate to [open an issue](https://github.com/itsmevictor/clean-transcribe/issues).
