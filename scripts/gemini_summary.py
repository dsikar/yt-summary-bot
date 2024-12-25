import sys
import argparse
from youtube_transcript_api import YouTubeTranscriptApi
import os
import google.generativeai as genai
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
        print(f"Error fetching transcript: {e}")
        return None

def request_gemini_summary(transcript):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        prompt = f"""Generate a markdown formatted digest of the following youtube transcript. 
        Include a brief summary and a bulleted list of main points:

        {transcript}"""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Request to Gemini API failed: {e}")
        return None

def save_output(video_id, content, success=True):
    """Save the output to a markdown file"""
    filename = f"gemini_{video_id}.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'w', encoding='utf-8') as f:
        if success:
            header = f"# gemini-1.5-pro_{video_id}\n\nTimestamp: {timestamp}\n\n---\n\n"
            f.write(header + content)
        else:
            f.write(f"# Summary Generation Failed\n\nVideo ID: {video_id}\nTimestamp: {timestamp}\n\nError: {content}")

def truncate_to_words(text, max_words):
    """Truncate text to specified number of words"""
    words = text.split()
    return ' '.join(words[:max_words])

def main():
    parser = argparse.ArgumentParser(description='Generate YouTube video summary using Gemini')
    parser.add_argument('video_id', help='YouTube video ID')
    parser.add_argument('--max-words', type=int, default=7000, help='Maximum number of words to process (default: 7000)')
    args = parser.parse_args()

    video_id = args.video_id
    
    # Fetch transcript
    transcript = get_youtube_transcript(video_id)
    if transcript is None:
        error_message = "Failed to fetch YouTube transcript"
        print(error_message)
        save_output(video_id, error_message, success=False)
        sys.exit(1)
    
    # Truncate transcript if needed
    truncated_transcript = truncate_to_words(transcript, args.max_words)
    
    # Request summary from Gemini
    summary = request_gemini_summary(truncated_transcript)
    if summary:
        print(summary)
        save_output(video_id, summary)
    else:
        error_message = "Failed to get summary from Gemini API."
        print(error_message)
        save_output(video_id, error_message, success=False)

if __name__ == "__main__":
    main()
