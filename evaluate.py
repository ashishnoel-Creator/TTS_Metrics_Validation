import os
import argparse
import pandas as pd
from tqdm import tqdm
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

from metrics.srmr_metric import calculate_srmr
from metrics.sigmos_metric import calculate_sigmos
from metrics.vqscore_metric import calculate_vqscore
from metrics.wvmos_metric import calculate_wvmos

METRIC_DESCRIPTIONS = {
    'SRMR': 'Technical measurement of reverberation and room acoustics',
    'SIGMOS_DISC': 'Audio continuity and smoothness',
    'VQScore': 'Overall voice quality assessment',
    'WVMOS': 'Predicted subjective quality rating',
    'SIGMOS_OVRL': 'Comprehensive overall audio quality',
    'SIGMOS_REVERB': 'Perceived reverberation quality'
}

THRESHOLDS = {
    'SRMR': 8.0,
    'SIGMOS_DISC': 4.0,
    'VQScore': 0.67,
    'WVMOS': 4.0,
    'SIGMOS_OVRL': 3.0,
    'SIGMOS_REVERB': 3.5
}

def evaluate_file(file_path):
    # Calculate all scores first
    scores = {}
    
    # SRMR
    scores['SRMR'] = calculate_srmr(file_path)
    
    # SIGMOS
    sigmos_scores = calculate_sigmos(file_path)
    if sigmos_scores:
        scores.update(sigmos_scores)
    else:
        scores['SIGMOS_DISC'] = None
        scores['SIGMOS_OVRL'] = None
        scores['SIGMOS_REVERB'] = None
        
    # VQScore
    scores['VQScore'] = calculate_vqscore(file_path)
    
    # WVMOS
    scores['WVMOS'] = calculate_wvmos(file_path)
    
    # Build list of rows for this file
    rows = []
    filename = os.path.basename(file_path)
    
    for metric, threshold in THRESHOLDS.items():
        score = scores.get(metric)
        
        if score is None:
            status = 'ERROR'
        elif score >= threshold:
            status = 'PASS'
        else:
            status = 'FAIL'
            
        row = {
            'Filename': filename,
            'Metric': metric,
            'Description': METRIC_DESCRIPTIONS.get(metric, ''),
            'Threshold': threshold,
            'Score': score,
            'PASS OR FAIL': status
        }
        rows.append(row)
        
    return rows

def main():
    parser = argparse.ArgumentParser(description='TTS Audio Quality Evaluation')
    parser.add_argument('input_path', help='Path to audio file or directory')
    parser.add_argument('--output', default='evaluation_report.csv', help='Output CSV file')
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
        print(f"Invalid path: {input_path}")
        return
    
    print(f"Found {len(files)} files to evaluate.")
    
    all_rows = []
    for file_path in tqdm(files):
        try:
            file_rows = evaluate_file(file_path)
            all_rows.extend(file_rows)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Failed to process {file_path}: {e}")
            
    df = pd.DataFrame(all_rows)
    
    # Ensure column order
    cols = ['Filename', 'Metric', 'Description', 'Threshold', 'Score', 'PASS OR FAIL']
    df = df[cols]
    
    df.to_csv(args.output, index=False)
    print(f"Report saved to {args.output}")

if __name__ == '__main__':
    main()
