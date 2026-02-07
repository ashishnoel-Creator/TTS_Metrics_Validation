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
    
    # Also clean up temp chunks if they exist
    for root, dirs, files in os.walk(INPUT_DIR):
        if "temp_smart_chunks" in dirs:
            chunks_path = os.path.join(root, "temp_smart_chunks")
            print(f"Cleaning up temp chunks: {chunks_path}")
            shutil.rmtree(chunks_path)

def run_analysis():
    # 1. Check if input directory exists
    if not os.path.exists(INPUT_DIR):
        print(f"Creating input directory: {INPUT_DIR}")
        os.makedirs(INPUT_DIR)
        print(f"Please put your audio files in '{INPUT_DIR}' and run this script again.")
        return

    # 2. Check if there are audio files (Recursive)
    files = []
    for root, dirs, filenames in os.walk(INPUT_DIR):
        for filename in filenames:
            if filename.lower().endswith(('.wav', '.mp3', '.flac')):
                files.append(os.path.join(root, filename))
                
    if not files:
        print(f"No audio files found in '{INPUT_DIR}' (checked subdirectories too). Please add some files.")
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
