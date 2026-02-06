import os
import shutil
import sys
import subprocess

# Configuration
INPUT_DIR = "input_audio"
OUTPUT_REPORT = "analysis_report.csv"
SCRIPT_PATH = "smart_evaluate.py"

def clean_previous_report():
    if os.path.exists(OUTPUT_REPORT):
        print(f"Cleaning up previous report: {OUTPUT_REPORT}")
        os.remove(OUTPUT_REPORT)

def run_analysis():
    # 1. Check if input directory exists
    if not os.path.exists(INPUT_DIR):
        print(f"Creating input directory: {INPUT_DIR}")
        os.makedirs(INPUT_DIR)
        print(f"Please put your audio files in '{INPUT_DIR}' and run this script again.")
        return

    # 2. Check if there are audio files
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.wav', '.mp3', '.flac'))]
    if not files:
        print(f"No audio files found in '{INPUT_DIR}'. Please add some files.")
        return

    # 3. Clean previous report
    clean_previous_report()

    # 4. Run smart_evaluate.py targeting the input directory
    print(f"Running analysis on {len(files)} files in '{INPUT_DIR}'...")
    cmd = [sys.executable, SCRIPT_PATH, INPUT_DIR, "--output", OUTPUT_REPORT]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ Analysis complete! Report saved to: {OUTPUT_REPORT}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Analysis failed: {e}")

if __name__ == "__main__":
    run_analysis()
