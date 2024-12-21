import sys
import subprocess
import time

def run_script(script_name, video_id):
    """Run a Python script with the given video ID and handle any errors"""
    print(f"\n=== Running {script_name} ===")
    try:
        subprocess.run(['python', f'scripts/{script_name}', video_id], check=True)
        print(f"✓ {script_name} completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running {script_name}: {e}")
        return False
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/orchestrate_analysis.py <video_id>")
        sys.exit(1)

    video_id = sys.argv[1]
    
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
        if run_script(script, video_id):
            success_count += 1
        time.sleep(1)  # Small delay between API calls
    
    # Only run comparison if at least two summaries were generated
    if success_count >= 2:
        print("\n=== Running comparison analysis ===")
        run_script('compare_and_contrast.py', video_id)
    else:
        print("\n⚠ Not enough successful summaries to run comparison analysis")

if __name__ == "__main__":
    main()
