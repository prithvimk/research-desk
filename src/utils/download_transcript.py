import sys
import argparse
import urllib.parse
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# Add project root to sys.path so 'src' module can be resolved when script is run directly
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.config import INBOX_DIR

def extract_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            p = urllib.parse.parse_qs(parsed_url.query)
            if 'v' in p:
                return p['v'][0]
        if parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        if parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    raise ValueError("Could not extract video ID from URL")

def download_transcript(url, output_filename=None):
    try:
        video_id = extract_video_id(url)
        print(f"Extracting transcript for video ID: {video_id}")
        
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        
        formatter = TextFormatter()
        text_formatted = formatter.format_transcript(transcript)
        
        if not output_filename:
            output_filename = f"transcript_{video_id}.txt"
            
        transcripts_dir = INBOX_DIR / "transcripts"
        transcripts_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = transcripts_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_formatted)
            
        print(f"Transcript successfully saved to {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download YouTube video transcript.")
    parser.add_argument("url", help="The YouTube video URL")
    parser.add_argument("-o", "--output", help="Output text file name (saved in inbox/transcripts)")
    
    args = parser.parse_args()
    download_transcript(args.url, args.output)
