import sys
import argparse
from youtube_transcript_api import YouTubeTranscriptApi
import os
from openai import OpenAI
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
            transcript = transcript_list.find_transcript(['en'])
            if not transcript:
                transcript = transcript_list[0]

        transcript_data = transcript.fetch()
        full_transcript = ' '.join([t['text'] for t in transcript_data if t['text'].strip()])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_transcript)
        
        return full_transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def request_openai_summary(transcript, source_lang=None, target_lang=None):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a YouTube transcript analyst.{' The input transcript is in ' + source_lang + ' language.' if source_lang else ''}{' Generate your response in ' + target_lang + ' language.' if target_lang else ''}"},
                {"role": "user", "content": f"Generate a markdown formatted digest of the following youtube transcript. Include a brief summary and a bulleted list of main points:\n\n{transcript}"},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Request to OpenAI API failed: {e}")
        return None

def save_output(video_id, content, source_lang=None, target_lang=None, success=True):
    """Save the output to a markdown file"""
    filename = f"openai_{video_id}"
    if source_lang:
        filename += f"_{source_lang}"
    if target_lang and target_lang != source_lang:
        filename += f"_to_{target_lang}"
    filename += ".md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'w', encoding='utf-8') as f:
        if success:
            word_count = len(content.split())
            header = f"# gpt-4_{video_id}\n\nTimestamp: {timestamp}\n\nTranscript word count: {word_count}\n\n---\n\n"
            f.write(header + content)
        else:
            f.write(f"# Summary Generation Failed\n\nVideo ID: {video_id}\nTimestamp: {timestamp}\n\nError: {content}")

def truncate_to_words(text, max_words):
    """Truncate text to specified number of words"""
    words = text.split()
    return ' '.join(words[:max_words])

def main():
    parser = argparse.ArgumentParser(description='Generate YouTube video summary using OpenAI')
    parser.add_argument('video_id', help='YouTube video ID')
    parser.add_argument('--max-words', type=int, default=22000, help='Maximum number of words to process (default: 22000)')
    parser.add_argument('--source-lang', help='Source language code (e.g., en, es, fr)')
    parser.add_argument('--target-lang', help='Target language code for translation')
    args = parser.parse_args()

    video_id = args.video_id
    source_lang = args.source_lang
    target_lang = args.target_lang or source_lang
    
    # Show available transcripts
    list_available_transcripts(video_id)
    
    print(f"\nFetching transcript for video ID: {video_id}...")
    # Fetch transcript
    transcript = get_youtube_transcript(video_id, source_lang, target_lang)
    if transcript:
        print(f"\nTranscript retrieved successfully! Length: {len(transcript)} characters")
    if transcript is None:
        error_message = "Failed to fetch YouTube transcript"
        print(error_message)
        save_output(video_id, error_message, success=False)
        sys.exit(1)
    
    # Get word counts
    original_word_count = len(transcript.split())
    
    print("\nRequesting summary from OpenAI GPT-4...")
    # Truncate transcript if needed
    truncated_transcript = truncate_to_words(transcript, args.max_words)
    truncated_word_count = len(truncated_transcript.split())
    
    # Add truncation notice if needed
    if truncated_word_count < original_word_count:
        print(f"\nTranscript truncated from {original_word_count} to {truncated_word_count} words")
    
    # Request summary from OpenAI
    summary = request_openai_summary(truncated_transcript, source_lang, target_lang)
    if summary:
        print("\nSummary generated successfully!")
        print("\n=== SUMMARY ===\n")
        print(summary)
        print("\n=============\n")
        save_output(video_id, summary, source_lang, target_lang)
        print(f"Summary saved to openai_{video_id}.md")
    else:
        error_message = "Failed to get summary from OpenAI API."
        print(error_message)
        save_output(video_id, error_message, success=False)

if __name__ == "__main__":
    main()
