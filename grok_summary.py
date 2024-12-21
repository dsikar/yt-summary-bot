import sys
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import json

def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = ' '.join([t['text'] for t in transcript if t['text'].strip()])
        return full_transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def request_grok_summary(transcript):
    api_key = 'XAI_API_KEY'
    url = 'https://api.x.ai/v1'  # Replace this with the actual API endpoint
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    body = {
        "prompt": f"Generate a markdown formatted digest of the following youtube transcript. Include a brief summary and a bulleted list of main points:\n\n{transcript}",
        "max_tokens": 1000  # Adjust based on your needs
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(body))
        response.raise_for_status()
        return response.json()['content']
    except requests.RequestException as e:
        print(f"Request to Grok API failed: {e}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <video_id>")
        sys.exit(1)

    video_id = sys.argv[1]
    
    # Fetch transcript
    transcript = get_youtube_transcript(video_id)
    if transcript is None:
        sys.exit(1)
    
    # Request summary from Grok
    summary = request_grok_summary(transcript)
    if summary:
        print(summary)
    else:
        print("Failed to get summary from Grok API.")

if __name__ == "__main__":
    main()
