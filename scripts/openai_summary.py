import sys
from youtube_transcript_api import YouTubeTranscriptApi
import os
from openai import OpenAI
from datetime import datetime

def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = ' '.join([t['text'] for t in transcript if t['text'].strip()])
        # Save transcript to file
        with open(f"{video_id}.txt", 'w', encoding='utf-8') as f:
            f.write(full_transcript)
        return full_transcript
    except Exception as e:
        print(f"\nError fetching transcript: {e}")
        return None

def request_openai_summary(transcript):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a YouTube transcript analyst."},
                {"role": "user", "content": f"Generate a markdown formatted digest of the following youtube transcript. Include a brief summary and a bulleted list of main points:\n\n{transcript}"},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Request to OpenAI API failed: {e}")
        return None

def save_output(video_id, content, success=True):
    """Save the output to a markdown file"""
    filename = f"openai_{video_id}.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'w', encoding='utf-8') as f:
        if success:
            header = f"# gpt-4_{video_id}\n\nTimestamp: {timestamp}\n\n---\n\n"
            f.write(header + content)
        else:
            f.write(f"# Summary Generation Failed\n\nVideo ID: {video_id}\nTimestamp: {timestamp}\n\nError: {content}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <video_id>")
        sys.exit(1)

    video_id = sys.argv[1]
    
    print(f"\nFetching transcript for video ID: {video_id}...")
    # Fetch transcript
    transcript = get_youtube_transcript(video_id)
    if transcript:
        print(f"\nTranscript retrieved successfully! Length: {len(transcript)} characters")
    if transcript is None:
        error_message = "Failed to fetch YouTube transcript"
        print(error_message)
        save_output(video_id, error_message, success=False)
        sys.exit(1)
    
    print("\nRequesting summary from OpenAI GPT-4...")
    # Request summary from OpenAI
    summary = request_openai_summary(transcript)
    if summary:
        print("\nSummary generated successfully!")
        print("\n=== SUMMARY ===\n")
        print(summary)
        print("\n=============\n")
        save_output(video_id, summary)
        print(f"Summary saved to openai_{video_id}.md")
    else:
        error_message = "Failed to get summary from OpenAI API."
        print(error_message)
        save_output(video_id, error_message, success=False)

if __name__ == "__main__":
    main()
