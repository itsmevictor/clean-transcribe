import subprocess

def trim_audio(input_path, output_path, start_time, end_time):
    """Trim an audio file using ffmpeg."""
    command = ['ffmpeg', '-y', '-i', input_path]
    if start_time:
        command.extend(['-ss', start_time])
    if end_time:
        command.extend(['-to', end_time])
    command.extend(['-c', 'copy', output_path])
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg error: {e.stderr}")
