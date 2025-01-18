import sys
import os
import glob
import argparse
from datetime import datetime
import glob
from anthropic import Anthropic
import google.generativeai as genai
from openai import OpenAI

def read_markdown_files(video_id, source_lang=None, target_lang=None):
    """Read all markdown summary files for a given video ID with language support"""
    summaries = {}
    base_patterns = ['claude', 'gemini', 'grok', 'openai', 'deepseek']
    
    for base in base_patterns:
        # Build filename pattern with language codes
        filename = f"{base}_{video_id}"
        if source_lang:
            filename += f"_{source_lang}"
        if target_lang and target_lang != source_lang:
            filename += f"_to_{target_lang}"
        filename += ".md"
        
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                summaries[filename] = f.read()
    
    return summaries

def format_comparison_prompt(summaries):
    """Format the summaries into a prompt for comparison"""
    prompt = "Compare and contrast the following AI-generated summaries. Analyze the differences in focus, detail level, and interpretation. Format your response in markdown with each file name as a section header:\n\n"
    
    for filename, content in summaries.items():
        prompt += f"# {filename}\n\n{content}\n\n"
    
    return prompt

def request_claude_comparison(summaries):
    CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    client = Anthropic(api_key=CLAUDE_API_KEY)
    
    try:
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            system="You are an analytical assistant comparing AI-generated summaries.",
            messages=[
                {
                    "role": "user",
                    "content": format_comparison_prompt(summaries)
                }
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Request to Claude API failed: {e}")
        return None

def request_gemini_comparison(summaries):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        response = model.generate_content(format_comparison_prompt(summaries))
        return response.text
    except Exception as e:
        print(f"Request to Gemini API failed: {e}")
        return None

def request_grok_comparison(summaries):
    XAI_API_KEY = os.getenv("XAI_API_KEY")
    client = OpenAI(
        api_key=XAI_API_KEY,
        base_url="https://api.x.ai/v1",
    )
    
    try:
        completion = client.chat.completions.create(
            model="grok-2-1212",
            messages=[
                {"role": "system", "content": "You are an analytical assistant comparing AI-generated summaries."},
                {"role": "user", "content": format_comparison_prompt(summaries)},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Request to Grok API failed: {e}")
        return None

def request_deepseek_comparison(summaries):
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1"
    )
    
    try:
        completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an analytical assistant comparing AI-generated summaries."},
                {"role": "user", "content": format_comparison_prompt(summaries)},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Request to DeepSeek API failed: {e}")
        return None

def request_openai_comparison(summaries):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an analytical assistant comparing AI-generated summaries."},
                {"role": "user", "content": format_comparison_prompt(summaries)},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Request to OpenAI API failed: {e}")
        return None

def save_comparison(video_id, model, content):
    """Save the comparison analysis to a markdown file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"summaries/comparison_{model}_{video_id}.md"
    
    # Ensure the summaries directory exists
    os.makedirs("summaries", exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        header = f"# AI Summary Comparison by {model}\n\nVideo ID: {video_id}\nTimestamp: {timestamp}\n\n---\n\n"
        f.write(header + content)

def update_readme(video_id, timestamp):
    """Update the README.md with links to the latest analysis files"""
    readme_path = "summaries/README.md"
    
    # Find all relevant files
    transcript_file = glob.glob(f"{video_id}*.txt")
    summary_files = glob.glob(f"summaries/*_{video_id}.md")
    comparison_files = glob.glob(f"summaries/comparison_*_{video_id}.md")
    
    # Create the new entry
    entry = f"\n## {timestamp}\n\n"
    
    if transcript_file:
        entry += "### Transcript\n"
        entry += f"- [{transcript_file[0]}]({transcript_file[0]})\n\n"
    
    if summary_files:
        entry += "### Summaries\n"
        for f in sorted(summary_files):
            if not f.startswith('comparison'):
                basename = os.path.basename(f)
                entry += f"- [{basename}]({basename})\n"
        entry += "\n"
    
    if comparison_files:
        entry += "### Comparisons\n"
        for f in sorted(comparison_files):
            basename = os.path.basename(f)
            entry += f"- [{basename}]({basename})\n"
        entry += "\n"
    
    # Append to README
    with open(readme_path, 'a', encoding='utf-8') as f:
        f.write(entry)

def main():
    parser = argparse.ArgumentParser(description='Compare AI-generated summaries')
    parser.add_argument('video_id', help='YouTube video ID')
    parser.add_argument('--source-lang', help='Source language code (e.g., en, es, fr)')
    parser.add_argument('--target-lang', help='Target language code for translation')
    args = parser.parse_args()

    video_id = args.video_id
    source_lang = args.source_lang
    target_lang = args.target_lang or source_lang
    
    summaries = read_markdown_files(video_id, source_lang, target_lang)
    
    if not summaries:
        print("No summary files found for the given video ID")
        sys.exit(1)
    
    # Get comparisons from each AI service
    services = {
        'claude': request_claude_comparison,
        'gemini': request_gemini_comparison,
        'grok': request_grok_comparison,
        'openai': request_openai_comparison,
        'deepseek': request_deepseek_comparison
    }
    
    for model, compare_func in services.items():
        print(f"\nRequesting comparison from {model}...")
        comparison = compare_func(summaries)
        if comparison:
            save_comparison(video_id, model, comparison)
            print(f"Saved {model}'s comparison analysis")
        else:
            print(f"Failed to get comparison from {model}")
    
    # Update README.md with links to all files
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    update_readme(video_id, timestamp)
    print("\nUpdated summaries/README.md with links to analysis files")

if __name__ == "__main__":
    main()
