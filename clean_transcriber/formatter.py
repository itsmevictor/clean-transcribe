def format_output(transcription_result, output_format):
    """Format transcription result into specified output format."""
    if output_format == 'txt':
        return format_txt(transcription_result)
    elif output_format == 'srt':
        return format_srt(transcription_result)
    elif output_format == 'vtt':
        return format_vtt(transcription_result)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

def format_txt(result):
    """Format as plain text."""
    return result['text'].strip()

def format_srt(result):
    """Format as SRT subtitle file."""
    srt_content = []
    
    for i, segment in enumerate(result['segments'], 1):
        start_time = format_timestamp_srt(segment['start'])
        end_time = format_timestamp_srt(segment['end'])
        text = segment['text'].strip()
        
        srt_content.append(f"{i}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(text)
        srt_content.append("")  # Empty line between segments
    
    return "\n".join(srt_content)

def format_vtt(result):
    """Format as WebVTT subtitle file."""
    vtt_content = ["WEBVTT", ""]
    
    for segment in result['segments']:
        start_time = format_timestamp_vtt(segment['start'])
        end_time = format_timestamp_vtt(segment['end'])
        text = segment['text'].strip()
        
        vtt_content.append(f"{start_time} --> {end_time}")
        vtt_content.append(text)
        vtt_content.append("")  # Empty line between segments
    
    return "\n".join(vtt_content)

def format_timestamp_srt(seconds):
    """Format timestamp for SRT format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def format_timestamp_vtt(seconds):
    """Format timestamp for VTT format (HH:MM:SS.mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"