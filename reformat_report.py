import pandas as pd

# Load the wide report
try:
    df = pd.read_csv('final_evaluation_report.csv')
except FileNotFoundError:
    print("final_evaluation_report.csv not found. Checking for Audio1/Audio2 reports...")
    # Fallback: try to read individual reports if the combined one is missing
    try:
        df1 = pd.read_csv('Audio1_report.csv')
        df2 = pd.read_csv('Audio2_report.csv')
        df = pd.concat([df1, df2])
    except Exception as e:
        print(f"Could not load reports: {e}")
        exit(1)

# Define metadata
METRICS = {
    'SRMR': {'desc': 'Technical measurement of reverberation and room acoustics', 'thresh': 8.0},
    'SIGMOS_DISC': {'desc': 'Audio continuity and smoothness', 'thresh': 4.0},
    'VQScore': {'desc': 'Overall voice quality assessment', 'thresh': 0.67},
    'WVMOS': {'desc': 'Predicted subjective quality rating', 'thresh': 4.0},
    'SIGMOS_OVRL': {'desc': 'Comprehensive overall audio quality', 'thresh': 3.0},
    'SIGMOS_REVERB': {'desc': 'Perceived reverberation quality', 'thresh': 3.5}
}

rows = []

for _, row in df.iterrows():
    filename = row['Filename']
    for metric, info in METRICS.items():
        # The column names in the wide CSV are like 'SRMR_Score', 'SRMR_Status'
        score = row.get(f'{metric}_Score')
        status = row.get(f'{metric}_Status')
        
        new_row = {
            'Filename': filename,
            'Metric': metric,
            'Description': info['desc'],
            'Threshold': info['thresh'],
            'Score': score,
            'PASS OR FAIL': status
        }
        rows.append(new_row)

# Create new DataFrame
new_df = pd.DataFrame(rows)
cols = ['Filename', 'Metric', 'Description', 'Threshold', 'Score', 'PASS OR FAIL']
new_df = new_df[cols]

# Save
new_df.to_csv('final_evaluation_report_formatted.csv', index=False)
print("Reformatted report saved to final_evaluation_report_formatted.csv")
