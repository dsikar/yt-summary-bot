import sys
import os
from googleapiclient.discovery import build

# Read the YouTube API key from environment variables
YOUTUBE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Ensure the API key is set
if not YOUTUBE_API_KEY:
    raise ValueError("Please set the YOUTUBE_API_KEY environment variable.")

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

def save_comments_to_file(video_id, comments):
    """
    Save the comments to a file named <video_id>_comments.txt.
    """
    try:
        filename = f"{video_id}_comments.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for comment in comments:
                f.write(f"{comment}\n\n")
        print(f"Comments saved to {filename}")
    except Exception as e:
        print(f"Error saving comments to file: {e}")

def main(video_id):
    # Step 1: Download comments
    print(f"Downloading comments for video ID: {video_id}...")
    comments = download_comments(video_id)
    if not comments:
        print("Failed to download comments.")
        return

    # Step 2: Save comments to file
    save_comments_to_file(video_id, comments)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download_comments.py <YouTube Video ID>")
        sys.exit(1)

    video_id = sys.argv[1]
    main(video_id)
