---
title: Audio Quality Analytics
emoji: 🎧
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.41.1
app_file: app.py
pinned: false
license: apache-2.0
---

# Audio Quality Analytics

## Simple Local Workflow (Automated)

1.  **Input**: Put your audio files (`.wav`, `.mp3`, `.flac`) into the `input_audio` folder.
2.  **Run**: Execute the analysis script:
    ```bash
    python run_local_analysis.py
    ```
3.  **Output**: Results will be saved to `analysis_report.csv`.

**Note**: running the script will automatically **delete** the previous `analysis_report.csv` before starting, ensuring you always get a fresh report for the current files in `input_audio`.

---

## Metric Details
- **SRMR**: Service, Room, and Modulation Quality. (Higher is better, >6.0)
- **SigMOS**: Signal Quality (Discontinuity, Overall, Reverb). (1-5 scale)
- **VQScore**: Voice Quality Score. (0-1 scale, >0.65)
- **WVMOS**: Waveform Mean Opinion Score. (1-5 scale, >1.5-3.0 depending on context)

## Metric Details
- **SRMR**: Service, Room, and Modulation Quality. (Higher is better, >6.0)
- **SigMOS**: Signal Quality (Discontinuity, Overall, Reverb). (1-5 scale)
- **VQScore**: Voice Quality Score. (0-1 scale, >0.65)
- **WVMOS**: Waveform Mean Opinion Score. (1-5 scale, >1.5-3.0 depending on context)

---

## Instructions for AI Agents
If you are an AI assistant helping the user:
1.  **Do NOT** read or modify `metrics/` unless explicitly asked.
2.  **To Run Analysis**:
    - Ask the user to place files in `input_audio/`.
    - Run `python run_local_analysis.py`.
    - Read the resulting `analysis_report.csv`.
    - **Important**: First time run requires downloading the WVMOS model:
      ```bash
      python download_wvmos.py
      ```

