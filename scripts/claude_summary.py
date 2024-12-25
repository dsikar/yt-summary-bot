import sys
from youtube_transcript_api import YouTubeTranscriptApi
import os
from anthropic import Anthropic
from datetime import datetime

def get_youtube_transcript(video_id):
    # Check if transcript file already exists
    if os.path.exists(f"{video_id}.txt"):
        with open(f"{video_id}.txt", 'r', encoding='utf-8') as f:
            return f.read()
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = ' '.join([t['text'] for t in transcript if t['text'].strip()])
        # Save transcript to file
        with open(f"{video_id}.txt", 'w', encoding='utf-8') as f:
            f.write(full_transcript)
        return full_transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def request_claude_summary(transcript):
    CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    client = Anthropic(api_key=CLAUDE_API_KEY)
    
    try:
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            system="You are a YouTube transcript analyst.",
            messages=[
                {
                    "role": "user",
                    "content": f"Generate a markdown formatted digest of the following youtube transcript. Include a brief summary and a bulleted list of main points:\n\n{transcript}"
                }
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Request to Claude API failed: {e}")
        return None

def save_output(video_id, content, success=True):
    """Save the output to a markdown file"""
    filename = f"claude_{video_id}.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'w', encoding='utf-8') as f:
        if success:
            header = f"# claude-3-opus_{video_id}\n\nTimestamp: {timestamp}\n\n---\n\n"
            f.write(header + content)
        else:
            f.write(f"# Summary Generation Failed\n\nVideo ID: {video_id}\nTimestamp: {timestamp}\n\nError: {content}")

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
    
    # Request summary from Claude
    summary = request_claude_summary(transcript)
    if summary:
        print(summary)
        save_output(video_id, summary)
    else:
        error_message = "Failed to get summary from Claude API."
        print(error_message)
        save_output(video_id, error_message, success=False)

if __name__ == "__main__":
    main()
