import sys
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
    
    # Request summary from Gemini
    summary = request_gemini_summary(transcript)
    if summary:
        print(summary)
        save_output(video_id, summary)
    else:
        error_message = "Failed to get summary from Gemini API."
        print(error_message)
        save_output(video_id, error_message, success=False)

if __name__ == "__main__":
    main()
