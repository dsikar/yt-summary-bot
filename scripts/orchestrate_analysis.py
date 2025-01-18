import sys
import subprocess
import time
import argparse

def run_script(script_name, video_id, source_lang=None, target_lang=None):
    """Run a Python script with the given video ID and language options, and handle any errors"""
    print(f"\n=== Running {script_name} ===")
    try:
        cmd = ['python', f'scripts/{script_name}']
        
        # Handle different argument patterns for different scripts
        if script_name == 'claude_summary.py':
            # Claude uses positional arguments
            cmd.extend([video_id])
            if source_lang:
                cmd.extend([source_lang])
            if target_lang:
                cmd.extend([target_lang])
        else:
            # Others use argparse style
            cmd.extend([video_id])
            if source_lang:
                cmd.extend(['--source-lang', source_lang])
            if target_lang:
                cmd.extend(['--target-lang', target_lang])
        
        subprocess.run(cmd, check=True)
        print(f"✓ {script_name} completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running {script_name}: {e}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description='Orchestrate YouTube video analysis across multiple AI models')
    parser.add_argument('video_id', help='YouTube video ID')
    parser.add_argument('--source-lang', help='Source language code (e.g., en, es, fr)')
    parser.add_argument('--target-lang', help='Target language code for translation')
    args = parser.parse_args()

    video_id = args.video_id
    source_lang = args.source_lang
    target_lang = args.target_lang or source_lang
    
    # List of summary scripts to run
    summary_scripts = [
        'claude_summary.py',
        'gemini_summary.py',
        'grok_summary.py',
        'openai_summary.py'
    ]
    
    # Run each summary script
    success_count = 0
    for script in summary_scripts:
        if run_script(script, video_id, source_lang, target_lang):
            success_count += 1
        time.sleep(1)  # Small delay between API calls
    
    # Only run comparison if at least two summaries were generated
    if success_count >= 2:
        print("\n=== Running comparison analysis ===")
        run_script('compare_and_contrast.py', video_id, source_lang, target_lang)
    else:
        print("\n⚠ Not enough successful summaries to run comparison analysis")

if __name__ == "__main__":
    main()
