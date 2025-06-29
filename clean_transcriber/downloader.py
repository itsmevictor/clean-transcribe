import yt_dlp
import os

def download_audio(url, output_dir, start_time=None, end_time=None):
    """Download audio from a YouTube URL."""
    
    postprocessor_args = []
    if start_time or end_time:
        if start_time:
            postprocessor_args.extend(["-ss", start_time])
        if end_time:
            postprocessor_args.extend(["-to", end_time])

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessor_args': postprocessor_args,
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_title = info_dict.get('title', None)
        
        # Construct the expected output filename
        base_name = ydl.prepare_filename(info_dict).rsplit('.', 1)[0]
        output_filename = f"{base_name}.mp3"
        
        return output_filename, video_title