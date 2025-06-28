from pydub import AudioSegment
import os

def extract_audio(video_path, output_dir):
    """Extract audio from a local video file using pydub and return its path."""
    try:
        video = AudioSegment.from_file(video_path)
        
        # Create a safe filename for the audio output
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_filename = f"{base_name}.mp3"
        audio_path = os.path.join(output_dir, audio_filename)
        
        # Export the audio
        video.export(audio_path, format="mp3")
        
        if os.path.exists(audio_path):
            return audio_path
        else:
            raise FileNotFoundError("Failed to extract audio from video.")
            
    except Exception as e:
        raise IOError(f"Error processing video file with pydub: {e}")