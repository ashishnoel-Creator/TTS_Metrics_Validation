import pandas as pd
import config
import os

THRESHOLDS = config.THRESHOLDS

def regrade_csv(file_path):
    if not os.path.exists(file_path):
        print(f"Skipping {file_path} (Not found)")
        return

    print(f"Regrading {file_path}...")
    df = pd.read_csv(file_path)
    
    # Iterate and update
    updated_rows = []
    
    for index, row in df.iterrows():
        metric = row['Metric']
        score = row['Score']
        
        # Determine new threshold
        threshold = THRESHOLDS.get(metric)
        
        if threshold is not None:
             # Update Threshold column
            row['Threshold'] = threshold
            
            # Update Status
            if score >= threshold:
                row['PASS OR FAIL'] = 'PASS'
            else:
                row['PASS OR FAIL'] = 'FAIL'
        
        updated_rows.append(row)
        
    new_df = pd.DataFrame(updated_rows)
    new_df.to_csv(file_path, index=False)
    print(f"Updated {file_path}")

if __name__ == "__main__":
    reports = [
        "brazil_sampled_report.csv",
        "probono_india_3_report.csv",
        "probono_india_4_report.csv",
        "haryanvi_sample_report.csv"
    ]
    
    for report in reports:
        regrade_csv(report)
