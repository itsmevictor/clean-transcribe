# YouTube Transcriber

A command-line tool that transcribes YouTube videos to text using OpenAI's Whisper model, with AI-powered transcript cleaning.

## Features

- Download audio from YouTube videos
- Transcribe using [OpenAI Whisper](https://github.com/openai/whisper) (multiple model sizes available)
- **AI-powered transcript cleaning** using various LLMs (Gemini, ChatGPT, Claude)
- Multiple output formats: TXT, SRT, VTT
- Language detection and manual specification
- Progress indicators
- Keep audio files option
- Save both raw and cleaned versions

## Installation

1. Clone or download this repository:
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Requirements

- Python 3.7+
- FFmpeg (required by yt-dlp for audio processing)
- LLM API key for transcript cleaning (optional but recommended)

## Usage

Basic usage:
```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Advanced options with cleaning:
```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" \
    --output transcript.txt \
    --format srt \
    --model medium \
    --language en \
    --clean \
    --llm-model gemini-2.0-flash-exp \
    --cleaning-style presentation \
    --save-raw \
    --keep-audio
```

### Options

**Basic Options:**
- `--output, -o`: Output file path (default: transcript.txt)
- `--format, -f`: Output format - txt, srt, or vtt (default: txt)
- `--model, -m`: Whisper model size - tiny, base, small, medium, large (default: base)
- `--language, -l`: Language code (auto-detect if not specified)
- `--keep-audio`: Keep the downloaded audio file

**Cleaning Options:**
- `--clean/--no-clean`: Enable/disable transcript cleaning (default: enabled)
- `--llm-model`: LLM model for cleaning (default: gemini-2.0-flash-exp)
- `--cleaning-style`: Style of cleaning - presentation, conversation, lecture (default: presentation)
- `--save-raw`: Also save the raw transcript before cleaning

### Model Sizes

- `tiny`: Fastest, least accurate (~39 MB)
- `base`: Good balance of speed and accuracy (~74 MB)
- `small`: Better accuracy (~244 MB)
- `medium`: High accuracy (~769 MB)
- `large`: Best accuracy (~1550 MB)

## LLM Setup for Transcript Cleaning

The tool uses the excellent `llm` [package developed by Simon Willison](https://github.com/simonw/llm) to support multiple AI providers. Set up your preferred provider:

### Google Gemini (Recommended)
```bash
llm install llm-gemini
llm keys set gemini
# Enter your Gemini API key when prompted
```

### OpenAI ChatGPT
```bash
llm keys set openai
# Enter your OpenAI API key when prompted
```

### Anthropic Claude
```bash
llm install llm-claude-3
llm keys set claude
# Enter your Anthropic API key when prompted
```

### Available Models
Check available models: `llm models`

Popular options:
- `gemini-2.0-flash-exp` (fast, cost-effective)
- `gpt-4o-mini` (OpenAI, fast)
- `gpt-4o` (OpenAI, high quality)
- `claude-3-5-sonnet-20241022` (Anthropic)

## Examples

Basic transcription with cleaning:
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Create cleaned SRT subtitles:
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -f srt -o subtitles.srt
```

Transcribe lecture with high-quality models:
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
    -m large \
    --llm-model gemini-2.0-flash-exp \
    --cleaning-style lecture \
    --save-raw
```

Disable cleaning for raw transcript:
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --no-clean
```

## Output Formats

- **TXT**: Plain text transcription (cleaned or raw)
- **SRT**: SubRip subtitle format with timestamps
- **VTT**: WebVTT subtitle format for web players

## Cleaning Styles

- **presentation**: Removes filler words, organizes into paragraphs, maintains professional tone
- **conversation**: Preserves conversational flow while cleaning up false starts and fillers  
- **lecture**: Optimized for educational content, creates clear sections suitable for study notes

## What Cleaning Does

The AI cleaning process:
1. Removes filler words (um, uh, so, like, you know, etc.)
2. Fixes grammar and punctuation errors
3. Organizes content into logical paragraphs
4. Maintains original meaning and tone
5. Preserves important emphasis and context
6. Makes the text more readable and professional

Note: For SRT/VTT formats, timing information is preserved but text is cleaned.

## Installation as Package

To install as a system command:
```bash
pip install -e .
```

Then use:
```bash
youtube-transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
```