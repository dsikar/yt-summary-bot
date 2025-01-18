import sys
from youtube_transcript_api import YouTubeTranscriptApi
import os
from anthropic import Anthropic
from datetime import datetime

def list_available_transcripts(video_id):
    """List all available transcript languages for a video"""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        print("\nAvailable transcripts:")
        print("=====================")
        for transcript in transcript_list:
            print(f"Language: {transcript.language} ({transcript.language_code})")
            print(f"- Generated: {'Yes' if transcript.is_generated else 'No'}")
            print(f"- Translation: {'Yes' if transcript.is_translatable else 'No'}")
            print("---------------------")
        return transcript_list
    except Exception as e:
        print(f"Error listing transcripts: {e}")
        return None

def get_youtube_transcript(video_id, source_lang=None, target_lang=None):
    """
    Get transcript for a video with optional translation
    source_lang: Original language to fetch (e.g., 'en', 'es', 'fr')
    target_lang: Language to translate to (if different from source)
    """
    # Check if cached transcript file already exists
    filename = f"{video_id}_{source_lang}"
    if target_lang and target_lang != source_lang:
        filename += f"_to_{target_lang}"
    filename += ".txt"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        if source_lang:
            try:
                transcript = transcript_list.find_transcript([source_lang])
            except:
                print(f"\nRequested language '{source_lang}' not found.")
                print("Available languages:")
                list_available_transcripts(video_id)
                return None
        else:
            # Get default language transcript
            transcript = transcript_list.find_transcript(['en'])  # Try English first
            if not transcript:
                transcript = transcript_list[0]  # Fall back to first available
        
        # Get the actual transcript
        transcript_data = transcript.fetch()
        full_transcript = ' '.join([t['text'] for t in transcript_data if t['text'].strip()])
        
        # Cache transcript with language code in filename if specified
        filename = f"{video_id}_{source_lang}.txt" if source_lang else f"{video_id}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_transcript)
        
        return full_transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def request_claude_summary(transcript, source_lang=None, target_lang=None):
    CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    client = Anthropic(api_key=CLAUDE_API_KEY)
    
    try:
        system_msg = "You are a YouTube transcript analyst."
        if source_lang:
            system_msg += f" The input transcript is in {source_lang} language."
        if target_lang:
            system_msg += f" Generate your response in {target_lang} language."
            
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            system=system_msg,
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

def save_output(video_id, content, source_lang=None, target_lang=None, success=True):
    """Save the output to a markdown file"""
    filename = f"summaries/claude_{video_id}"
    if source_lang:
        filename += f"_{source_lang}"
    if target_lang and target_lang != source_lang:
        filename += f"_to_{target_lang}"
    filename += ".md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'w', encoding='utf-8') as f:
        if success:
            header = f"# claude-3-opus_{video_id}\n\nTimestamp: {timestamp}\n\n---\n\n"
            f.write(header + content)
        else:
            f.write(f"# Summary Generation Failed\n\nVideo ID: {video_id}\nTimestamp: {timestamp}\n\nError: {content}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <video_id> [source_lang] [target_lang]")
        print("Example: python script.py dQw4w9WgXcQ es en")
        sys.exit(1)

    video_id = sys.argv[1]
    source_lang = sys.argv[2] if len(sys.argv) > 2 else None
    target_lang = sys.argv[3] if len(sys.argv) > 3 else source_lang

    # Show available transcripts
    list_available_transcripts(video_id)
    
    # Fetch transcript in specified language
    transcript = get_youtube_transcript(video_id, source_lang, target_lang)
    if transcript is None:
        error_message = "Failed to fetch YouTube transcript"
        print(error_message)
        save_output(video_id, error_message, success=False)
        sys.exit(1)
    
    # Request summary from Claude
    summary = request_claude_summary(transcript, source_lang, target_lang)
    if summary:
        print(summary)
        save_output(video_id, summary)
    else:
        error_message = "Failed to get summary from Claude API."
        print(error_message)
        save_output(video_id, error_message, success=False)

if __name__ == "__main__":
    main()
