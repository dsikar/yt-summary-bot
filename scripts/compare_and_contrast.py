import sys
import os
import glob
from datetime import datetime
from anthropic import Anthropic
import google.generativeai as genai
from openai import OpenAI

def read_markdown_files(video_id):
    """Read all markdown summary files for a given video ID"""
    summaries = {}
    patterns = [
        f"claude_{video_id}.md",
        f"gemini_{video_id}.md",
        f"grok_{video_id}.md",
        f"openai_{video_id}.md"
    ]
    
    for pattern in patterns:
        if os.path.exists(pattern):
            with open(pattern, 'r', encoding='utf-8') as f:
                summaries[pattern] = f.read()
    
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
    filename = f"comparison_{model}_{video_id}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        header = f"# AI Summary Comparison by {model}\n\nVideo ID: {video_id}\nTimestamp: {timestamp}\n\n---\n\n"
        f.write(header + content)

def main():
    if len(sys.argv) != 2:
        print("Usage: python compare_and_contrast.py <video_id>")
        sys.exit(1)

    video_id = sys.argv[1]
    summaries = read_markdown_files(video_id)
    
    if not summaries:
        print("No summary files found for the given video ID")
        sys.exit(1)
    
    # Get comparisons from each AI service
    services = {
        'claude': request_claude_comparison,
        'gemini': request_gemini_comparison,
        'grok': request_grok_comparison,
        'openai': request_openai_comparison
    }
    
    for model, compare_func in services.items():
        print(f"\nRequesting comparison from {model}...")
        comparison = compare_func(summaries)
        if comparison:
            save_comparison(video_id, model, comparison)
            print(f"Saved {model}'s comparison analysis")
        else:
            print(f"Failed to get comparison from {model}")

if __name__ == "__main__":
    main()
