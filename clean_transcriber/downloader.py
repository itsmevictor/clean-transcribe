import yt_dlp
import os
import sys
import io
from contextlib import redirect_stderr

def download_audio(url, output_dir, start_time=None, end_time=None, cookies=None, cookies_from_browser=None):
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
        'ignoreerrors': False,
    }
    
    # Add cookie configuration if provided
    if cookies:
        ydl_opts['cookiefile'] = cookies
    elif cookies_from_browser:
        ydl_opts['cookiesfrombrowser'] = (cookies_from_browser,)

    try:
        # Capture stderr to prevent yt-dlp from showing errors before our clean message
        stderr_capture = io.StringIO()
        with redirect_stderr(stderr_capture):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_title = info_dict.get('title', None)
                
                # Construct the expected output filename
                base_name = ydl.prepare_filename(info_dict).rsplit('.', 1)[0]
                output_filename = f"{base_name}.mp3"
                
                return output_filename, video_title
    except yt_dlp.DownloadError as e:
        error_msg = str(e).lower()
        if any(phrase in error_msg for phrase in ['sign in', 'not a bot', 'private', 'age-restricted', 'members-only']):
            clean_message = (
                "> Authentication Required\n\n"
                "This video requires authentication (age-restricted, private, or members-only content).\n\n"
                "Solutions:\n"
                "  • Use browser cookies: --cookies-from-browser chrome\n"
                "  • Use cookie file: --cookies /path/to/cookies.txt\n\n"
                "> Documentation: https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies\n"
                "> Warning: Using cookies may risk temporary or permanent account suspension.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "yt-dlp error:\n"
                f"{str(e)}"
            )
            raise Exception(clean_message)
        else:
            raise e