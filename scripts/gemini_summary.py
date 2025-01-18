import sys
import argparse
from youtube_transcript_api import YouTubeTranscriptApi
import os
import google.generativeai as genai
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

def request_gemini_summary(transcript, source_lang=None, target_lang=None):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        system_prompt = "You are a YouTube transcript analyst."
        if source_lang:
            system_prompt += f" The input transcript is in {source_lang} language."
        if target_lang:
            system_prompt += f" Generate your response in {target_lang} language."
        
        prompt = f"""{system_prompt}
        
        Generate a markdown formatted digest of the following youtube transcript. 
        Include a brief summary and a bulleted list of main points:

        {transcript}"""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Request to Gemini API failed: {e}")
        return None

def save_output(video_id, content, source_lang=None, target_lang=None, success=True):
    """Save the output to a markdown file"""
    filename = f"summaries/gemini_{video_id}"
    if source_lang:
        filename += f"_{source_lang}"
        if target_lang and target_lang != source_lang:
            filename += f"_to_{target_lang}"
    filename += ".md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'w', encoding='utf-8') as f:
        if success:
            word_count = len(content.split())
            header = f"# gemini-1.5-pro_{video_id}\n\nTimestamp: {timestamp}\n\nTranscript word count: {word_count}\n\n---\n\n"
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
    parser.add_argument('--source-lang', help='Source language code (e.g., en, es, fr)')
    parser.add_argument('--target-lang', help='Target language code for translation')
    args = parser.parse_args()

    video_id = args.video_id
    source_lang = args.source_lang
    target_lang = args.target_lang or source_lang
    
    # Show available transcripts
    list_available_transcripts(video_id)
    
    # Fetch transcript
    transcript = get_youtube_transcript(video_id, source_lang, target_lang)
    if transcript is None:
        error_message = "Failed to fetch YouTube transcript"
        print(error_message)
        save_output(video_id, error_message, success=False)
        sys.exit(1)
    
    # Get word counts
    original_word_count = len(transcript.split())
    
    # Truncate transcript if needed
    truncated_transcript = truncate_to_words(transcript, args.max_words)
    truncated_word_count = len(truncated_transcript.split())
    
    # Add truncation notice if needed
    if truncated_word_count < original_word_count:
        print(f"\nTranscript truncated from {original_word_count} to {truncated_word_count} words")
    
    # Request summary from Gemini
    summary = request_gemini_summary(truncated_transcript, source_lang, target_lang)
    if summary:
        print(summary)
        save_output(video_id, summary)
    else:
        error_message = "Failed to get summary from Gemini API."
        print(error_message)
        save_output(video_id, error_message, success=False)

if __name__ == "__main__":
    main()
