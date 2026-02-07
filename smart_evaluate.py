import os
import argparse
import pandas as pd
import librosa
import soundfile as sf
import numpy as np
import traceback
from tqdm import tqdm
from evaluate import evaluate_file

import config
THRESHOLDS = config.THRESHOLDS

METRIC_DESCRIPTIONS = {
    'SRMR': 'Technical measurement of reverberation and room acoustics',
    'SIGMOS_DISC': 'Audio continuity and smoothness',
    'VQScore': 'Overall voice quality assessment',
    'WVMOS': 'Predicted subjective quality rating',
    'SIGMOS_OVRL': 'Comprehensive overall audio quality',
    'SIGMOS_REVERB': 'Perceived reverberation quality'
}

def process_file_smart(input_path, max_chunks=None, force_full=False):
    print(f"Processing {input_path}...")
    
    try:
        # Get metadata
        info = sf.info(input_path)
        sr = info.samplerate
        duration_sec = info.duration
        print(f"Total Duration: {duration_sec/60:.2f} mins")
        
        # Smart Sampling (Default) vs Full Analysis
        if force_full:
            print("Force Full: Analyzing full duration...")
            chunk_paths = [input_path]
        elif duration_sec > 180: # > 3 minutes
            num_chunks = 5
            chunk_duration = 30.0
            print(f"Large file. Using Smart Sampling ({num_chunks} chunks of {chunk_duration}s)...")
            
            # Create chunks list
            chunk_paths = []
            segment_length = duration_sec / num_chunks
            
            # Ensure chunks temp dir
            chunks_dir = os.path.join(os.path.dirname(input_path), "temp_smart_chunks")
            os.makedirs(chunks_dir, exist_ok=True)
            
            for i in range(num_chunks):
                # Center of the segment
                segment_center = (i * segment_length) + (segment_length / 2)
                start_time = max(0, segment_center - (chunk_duration / 2))
                
                # Boundary checks
                if start_time + chunk_duration > duration_sec:
                    start_time = max(0, duration_sec - chunk_duration)
                
                try:
                    y_chunk, sr_chunk = librosa.load(input_path, sr=None, offset=start_time, duration=chunk_duration)
                    chunk_filename = f"{os.path.basename(input_path)}_chunk_{i}.wav"
                    chunk_path = os.path.join(chunks_dir, chunk_filename)
                    sf.write(chunk_path, y_chunk, sr_chunk)
                    chunk_paths.append(chunk_path)
                except Exception as e:
                    print(f"Error extracting chunk {i}: {e}")
                    
            if not chunk_paths:
                print("Warning: Sampling failed, falling back to full file.")
                chunk_paths = [input_path]
        else:
            print("Short file. Analyzing full duration...")
            chunk_paths = [input_path]
        
        chunk_scores = {metric: [] for metric in THRESHOLDS.keys()}
        
        for chunk_path in chunk_paths:
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
                print(f"Error evaluating chunk {chunk_path}: {e}")
            
        # Calculate averages for THIS file (single chunk, so average is just the score)
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
        
        return file_rows

    except Exception as e:
        print(f"Failed to process file {input_path}: {e}")
        traceback.print_exc()
        return []

def main():
    parser = argparse.ArgumentParser(description='Smart Audio Evaluation (Aggregated)')
    parser.add_argument('input_path', help='Path to input audio file or directory')
    parser.add_argument('--output', default='smart_avg_report.csv', help='Output CSV file')
    parser.add_argument('--max-chunks', type=int, default=None, help='Maximum number of chunks to evaluate per file')
    parser.add_argument('--full', action='store_true', help='Force full-file analysis (disable sampling)')
    
    args = parser.parse_args()
    input_path = args.input_path
    
    files = []
    if os.path.isdir(input_path):
        for root, dirs, filenames in os.walk(input_path):
            for filename in filenames:
                if 'temp_smart_chunks' in root:
                    continue
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
        file_rows = process_file_smart(file_path, max_chunks=args.max_chunks, force_full=args.full)
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
