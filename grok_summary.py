import sys
from youtube_transcript_api import YouTubeTranscriptApi
import os
from openai import OpenAI
from datetime import datetime

def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = ' '.join([t['text'] for t in transcript if t['text'].strip()])
        return full_transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def request_grok_summary(transcript):
    XAI_API_KEY = os.getenv("XAI_API_KEY")
    client = OpenAI(
        api_key=XAI_API_KEY,
        base_url="https://api.x.ai/v1",
    )
    
    try:
        completion = client.chat.completions.create(
            model="grok-2-1212",
            messages=[
                {"role": "system", "content": "You are a YouTube transcript analyst."},
                {"role": "user", "content": f"Generate a markdown formatted digest of the following youtube transcript. Include a brief summary and a bulleted list of main points:\n\n{transcript}"},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Request to Grok API failed: {e}")
        return None

def save_output(video_id, content, success=True):
    """Save the output to a markdown file"""
    filename = f"{video_id}.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'w', encoding='utf-8') as f:
        if success:
            f.write(content)
        else:
            f.write(f"# Summary Generation Failed\n\nTimestamp: {timestamp}\n\nError: {content}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <video_id>")
        sys.exit(1)

    video_id = sys.argv[1]
    
    # Fetch transcript
    transcript = get_youtube_transcript(video_id)
    if transcript is None:
        error_message = "Failed to fetch YouTube transcript"
        print(error_message)
        save_output(video_id, error_message, success=False)
        sys.exit(1)
    
    # Request summary from Grok
    summary = request_grok_summary(transcript)
    if summary:
        print(summary)
        save_output(video_id, summary)
    else:
        error_message = "Failed to get summary from Grok API."
        print(error_message)
        save_output(video_id, error_message, success=False)

if __name__ == "__main__":
    main()
