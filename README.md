# YouTube Video Analysis Scripts

A collection of Python scripts for analyzing YouTube video transcripts using various AI models.

## Scripts

- `scripts/claude_summary.py` - Generates video summaries using Claude 3 Opus
- `scripts/gemini_summary.py` - Generates video summaries using Gemini 1.5 Pro
- `scripts/grok_summary.py` - Generates video summaries using Grok 2
- `scripts/openai_summary.py` - Generates video summaries using GPT-4
- `scripts/compare_and_contrast.py` - Compares summaries from all AI models

## Usage

1. Set up your environment variables:
   ```bash
   export ANTHROPIC_API_KEY="your-key"
   export GEMINI_API_KEY="your-key"
   export XAI_API_KEY="your-key"
   export OPENAI_API_KEY="your-key"
   ```

2. Generate summaries for a video:
   ```bash
   python scripts/claude_summary.py <video_id>
   python scripts/gemini_summary.py <video_id>
   python scripts/grok_summary.py <video_id>
   python scripts/openai_summary.py <video_id>
   ```

3. Compare the generated summaries:
   ```bash
   python scripts/compare_and_contrast.py <video_id>
   ```

## Output

Each script generates a markdown file with the following naming convention:
- `<model>_<video_id>.md` - Individual summaries
- `comparison_<model>_<video_id>.md` - Comparison analysis

The transcript is also saved as `<video_id>.txt`

## Environment Setup

1. Install pyenv if you haven't already:
   ```bash
   curl https://pyenv.run | bash
   ```

2. Create a Python virtual environment:
   ```bash
   pyenv install 3.9.5
   pyenv virtualenv 3.9.5 transcript-env
   ```

3. Set up local Python version:
   ```bash
   echo "transcript-env" > .python-version
   ```
   This will automatically activate the environment when you enter the directory.

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Requirements

- Python 3.9.5
- See requirements.txt for all dependencies
