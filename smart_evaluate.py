import os
import argparse
import pandas as pd
import librosa
import soundfile as sf
import numpy as np
import traceback
from tqdm import tqdm
from evaluate import evaluate_file

# Reuse thresholds from evaluate.py (defining here to avoid import issues if evaluate.py changes)
THRESHOLDS = {
    'SRMR': 8.0,
    'SIGMOS_DISC': 4.0,
    'VQScore': 0.67,
    'WVMOS': 4.0,
    'SIGMOS_OVRL': 3.0,
    'SIGMOS_REVERB': 3.5
}

METRIC_DESCRIPTIONS = {
    'SRMR': 'Technical measurement of reverberation and room acoustics',
    'SIGMOS_DISC': 'Audio continuity and smoothness',
    'VQScore': 'Overall voice quality assessment',
    'WVMOS': 'Predicted subjective quality rating',
    'SIGMOS_OVRL': 'Comprehensive overall audio quality',
    'SIGMOS_REVERB': 'Perceived reverberation quality'
}

def process_file_smart(input_path):
    print(f"Processing {input_path}...")
    
    try:
        # Load audio
        # print("Loading audio...")
        y, sr = librosa.load(input_path, sr=None)
        
        total_samples = len(y)
        duration_min = (total_samples / sr) / 60
        print(f"Duration: {duration_min*60:.2f}s")
        
        y_nonsilent = y # Keep original audio without silence removal
        
        # Determine chunks: 5-10 based on length (e.g., 1 chunk per minute, clamped)
        # If < 5 mins, use 5 chunks. If > 10 mins, use 10 chunks.
        num_chunks = max(5, min(10, int(duration_min)))
        if duration_min < 1.0: # If less than 1 min, stick to 5 chunks or even fewer if very short? keeping 5 for now.
             num_chunks = 5

        # Split into N chunks
        chunk_samples = total_samples // num_chunks
        
        # We put chunks in a temp folder relative to the file to avoid clutter
        chunks_dir = os.path.join(os.path.dirname(input_path), "temp_smart_chunks", os.path.splitext(os.path.basename(input_path))[0])
        os.makedirs(chunks_dir, exist_ok=True)
        
        chunk_scores = {metric: [] for metric in THRESHOLDS.keys()}
        
        # print(f"Splitting into {num_chunks} chunks...")
        for i in range(num_chunks):
            start = i * chunk_samples
            end = start + chunk_samples if i < num_chunks - 1 else total_samples
            
            y_chunk = y_nonsilent[start:end]
            
            chunk_filename = f"chunk_{i+1:02d}.wav"
            chunk_path = os.path.join(chunks_dir, chunk_filename)
            
            sf.write(chunk_path, y_chunk, sr)
            
            try:
                # Run existing evaluation logic
                rows = evaluate_file(chunk_path)
                # Collect scores
                for row in rows:
                    metric = row['Metric']
                    score = row['Score']
                    if score is not None:
                        chunk_scores[metric].append(score)
            except Exception as e:
                print(f"Error evaluating chunk {i+1} for {input_path}: {e}")
                
        # Calculate averages for THIS file
        file_rows = []
        filename = os.path.basename(input_path)
        
        for metric, values in chunk_scores.items():
            if values:
                avg_score = sum(values) / len(values)
                threshold = THRESHOLDS[metric]
                
                if avg_score >= threshold:
                    status = 'PASS'
                else:
                    status = 'FAIL'
                    
                row = {
                    'Filename': filename,
                    'Metric': metric,
                    'Description': METRIC_DESCRIPTIONS.get(metric, ''),
                    'Threshold': threshold,
                    'Score': avg_score,
                    'PASS OR FAIL': status
                }
                file_rows.append(row)
        
        # Cleanup chunks to save space? Optional.
        # import shutil
        # shutil.rmtree(chunks_dir)
        
        return file_rows

    except Exception as e:
        print(f"Failed to process file {input_path}: {e}")
        traceback.print_exc()
        return []

def main():
    parser = argparse.ArgumentParser(description='Smart Audio Evaluation (Aggregated)')
    parser.add_argument('input_path', help='Path to input audio file or directory')
    parser.add_argument('--output', default='smart_avg_report.csv', help='Output CSV file')
    
    args = parser.parse_args()
    input_path = args.input_path
    
    files = []
    if os.path.isdir(input_path):
        for root, dirs, filenames in os.walk(input_path):
            for filename in filenames:
                if filename.lower().endswith(('.wav', '.mp3', '.flac')):
                    files.append(os.path.join(root, filename))
    elif os.path.isfile(input_path):
        files.append(input_path)
    else:
        print(f"Error: Invalid path {input_path}")
        return

    print(f"Found {len(files)} files to evaluate.")
    
    all_rows = []
    for file_path in tqdm(files):
        file_rows = process_file_smart(file_path)
        all_rows.extend(file_rows)
        
    # Save master report
    df = pd.DataFrame(all_rows)
    # Ensure column order
    cols = ['Filename', 'Metric', 'Description', 'Threshold', 'Score', 'PASS OR FAIL']
    df = df[cols] if not df.empty else pd.DataFrame(columns=cols)
    
    df.to_csv(args.output, index=False)
    print(f"Report saved to {args.output}")

if __name__ == '__main__':
    main()
