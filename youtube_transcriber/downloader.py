import yt_dlp
import os
from pathlib import Path
import click

def download_audio(url, output_dir, start_time=None, end_time=None):
    """Download audio from YouTube URL using yt-dlp and return its path and title."""
    output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'extractaudio': True,
        'audioformat': 'mp3',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    if start_time or end_time:
        postprocessor_args = []
        if start_time:
            postprocessor_args.extend(['-ss', start_time])
        if end_time:
            postprocessor_args.extend(['-to', end_time])
        
        ydl_opts['postprocessor_args'] = postprocessor_args
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Get video info to determine output filename
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'audio')
        
        # Sanitize filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        audio_filename = f"{safe_title}.mp3"
        audio_path = os.path.join(output_dir, audio_filename)
        
        # Update the output template to use the sanitized name
        ydl_opts['outtmpl'] = os.path.join(output_dir, audio_filename.replace('.mp3', '.%(ext)s'))

        # Download the audio
        ydl.download([url])
        
        # The file should now be at the expected path
        if os.path.exists(audio_path):
            return audio_path, title
        
        # Fallback if the filename is unexpected
        for file in os.listdir(output_dir):
            if file.endswith('.mp3'):
                actual_path = os.path.join(output_dir, file)
                if actual_path != audio_path:
                    os.rename(actual_path, audio_path)
                return audio_path, title
        
        raise FileNotFoundError("Downloaded audio file not found")