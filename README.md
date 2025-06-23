# YouTube Transcriber

A command-line tool to turn any YouTube video into a clean, readable text transcript. It uses OpenAI's Whisper for transcription and the LLM of your choice to automatically clean and reformat the output.

## Features

1. **Automatic download** from YouTube
1. **Fast and accurate transcription** using OpenAI's Whisper models
2. **LLM-powered cleaning** that removes filler words, fixes grammar, and organizes content into readable paragraphs
3. **Multiple output formats** (TXT, SRT, VTT) for any use case
4. **Flexible LLM support** - use Gemini, ChatGPT, Claude or any other (local) LLM for cleaning

## Quick Start

```bash
# Basic usage - transcribe and clean
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Create clean subtitles
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" -f srt -o subtitles.srt
```

## Installation

**Option 1: Clone and run**
```bash
git clone https://github.com/itsmevictor/youtube-to-text
cd youtube-to-text
pip install -r requirements.txt
```

**Option 2: Install as package**
```bash
pip install -e .
youtube-transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Requirements:**
- Python 3.7+
- FFmpeg (for audio processing)
- LLM API key (for cleaning, optional but recommended)

## Usage Examples

**Basic transcription with cleaning:**
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Create clean subtitles:**
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -f srt -o subtitles.srt
```

**High-quality lecture transcription:**
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
    -m large \
    --llm-model gemini-2.0-flash-exp \
    --cleaning-style lecture \
    --save-raw
```

**Raw transcript (no cleaning):**
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --no-clean
```

## Configuration

### Key Options
- `--format, -f`: Output format (txt, srt, vtt)
- `--model, -m`: Whisper model (tiny, base, small, medium, large, turbo)
- `--llm-model`: LLM for cleaning (gemini-2.0-flash-exp, gpt-4o-mini, etc.)
- `--cleaning-style`: presentation, conversation, or lecture
- `--save-raw`: Keep both raw and cleaned versions
- `--no-clean`: Skip AI cleaning

### Whisper Models
| Model | Speed | Accuracy | Size | Notes |
|-------|-------|----------|------|-------|
| tiny | Fastest | Basic | ~39 MB | Quick transcripts |
| base | Fast | Good | ~74 MB | Balanced option |
| turbo | Fast | Very Good | ~809 MB | **Default** |
| large | Slow | Best | ~1550 MB | Highest quality |

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