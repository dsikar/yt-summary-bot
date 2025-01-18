import sys
import os
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from openai import OpenAI  # Import the OpenAI SDK

# Read API keys from environment variables
YOUTUBE_API_KEY = os.getenv("GOOGLE_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Ensure API keys are set
if not YOUTUBE_API_KEY or not DEEPSEEK_API_KEY:
    raise ValueError("Please set the YOUTUBE_API_KEY and DEEPSEEK_API_KEY environment variables.")

def download_transcript(video_id):
    """
    Download the transcript of a YouTube video using youtube_transcript_api.
    """
    try:
        # Fetch the English transcript
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])  # Try English first
        if not transcript:
            print("No English transcript found.")
            return None

        # Fetch the transcript data
        transcript_data = transcript.fetch()
        full_transcript = ' '.join([t['text'] for t in transcript_data if t['text'].strip()])
        return full_transcript
    except Exception as e:
        print(f"Error downloading transcript: {e}")
        return None

def download_comments(video_id):
    """
    Download comments from a YouTube video using the YouTube Data API.
    """
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        comments = []
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
            maxResults=100  # Adjust as needed
        )
        while request:
            response = request.execute()
            for item in response["items"]:
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment)
            request = youtube.commentThreads().list_next(request, response)
        return comments
    except Exception as e:
        print(f"Error downloading comments: {e}")
        return None

def send_to_deepseek(transcript, comments):
    """
    Send the transcript and comments to DeepSeek API for analysis.
    """
    try:
        # Initialize the OpenAI client for DeepSeek
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

        # Prepare the prompt
        prompt = (
            "Analyze the following YouTube video transcript and comments. "
            "Provide a markdown-formatted summary of the video's content and "
            "the general sentiment in the comments, outlining the main trends and opinions.\n\n"
            f"Transcript:\n{transcript}\n\nComments:\n{comments}"
        )

        # Send the request to DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",  # Use the correct model name
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            stream=False  # Set to True if you want streaming responses
        )

        # Extract and return the response content
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error sending data to DeepSeek: {e}")
        return None

def main(video_id):
    # Step 1: Download transcript
    print("Downloading transcript...")
    transcript = download_transcript(video_id)
    if not transcript:
        print("Failed to download transcript.")
        return

    # Step 2: Download comments
    print("Downloading comments...")
    comments = download_comments(video_id)
    if not comments:
        print("Failed to download comments.")
        return

    # Step 3: Send data to DeepSeek API
    print("Sending data to DeepSeek API...")
    analysis = send_to_deepseek(transcript, comments)
    if not analysis:
        print("Failed to get analysis from DeepSeek.")
        return

    # Step 4: Save or display the result
    print("\nAnalysis Result:\n")
    print(analysis)

    # Optionally, save the result to a file
    with open(f"{video_id}_analysis.md", "w") as f:
        f.write(analysis)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <YouTube Video ID>")
        sys.exit(1)

    video_id = sys.argv[1]
    main(video_id)
