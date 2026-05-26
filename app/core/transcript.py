from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
import re

# This method is for extracting the id of the vidio from various URL patterns
def extract_video_id(url: str) -> str:
    patterns = [
        r"[?&]v=([0-9A-Za-z_-]{11})",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"embed\/([0-9A-Za-z_-]{11})",
        r"shorts\/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")

# This method is the responsible for getting the transcription from the video
def get_transcript(url: str) -> dict:
    video_id = extract_video_id(url)
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list =ytt_api.list(video_id)
        # Try to find a manually created transcript first (better quality)
        try:
            transcript = transcript_list.find_manually_created_transcript(['en', 'ar', 'fr', 'de', 'es', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'])
        except NoTranscriptFound:
            # Fall back to auto generated transcription
            transcript = next(iter(transcript_list))


        fetched = transcript.fetch()
        language = transcript.language
        language_code = transcript.language_code

        # Format Transcription into clean code

        formatter = TextFormatter()
        text = formatter.format_transcript(fetched)

        # Clean white space
        text = re.sub(r'\s+', ' ', text).strip()
        return {
            "video_id": video_id,
            "text": text,
            "language": language,
            "language_code": language_code,
            "chunk_raw": fetched
        }
    except TranscriptsDisabled:
        raise ValueError(f"Transcripts disabled: {video_id}")
    except NoTranscriptFound:
        raise ValueError(f"Transcripts not found: {video_id}")
    except Exception as e:
        raise ValueError(f"Error fetching transcript: {str(e)}")