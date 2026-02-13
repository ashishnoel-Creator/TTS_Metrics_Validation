import streamlit as st
import os
import pandas as pd
import tempfile
import soundfile as sf
import shutil
import librosa
import numpy as np

# Import your existing metrics
# Using try-except blocks to handle potential import errors gracefully in the UI
# Metric imports moved to analysis block to prevent slow startup (Health Check Timeouts)


# Page Config
st.set_page_config(
    page_title="Audio Quality Analytics",
    page_icon="🎧",
    layout="wide"
)

# --- CSS to Hide Streamlit UI Elements ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

import config

# Use thresholds from config file
THRESHOLDS = config.THRESHOLDS
METRIC_DESCRIPTIONS = config.METRIC_DESCRIPTIONS

# Display Thresholds in Sidebar (Read-Only)
st.sidebar.title("⚙️ Metric Standards")
st.sidebar.markdown("### Passing Criteria")
st.sidebar.info("These thresholds are set by the administrator.")
st.sidebar.table(pd.DataFrame(list(THRESHOLDS.items()), columns=['Metric', 'Min Score']).set_index('Metric'))


METRIC_DESCRIPTIONS = {
    'SRMR': 'Technical measurement of reverberation and room acoustics',
    'SIGMOS_DISC': 'Audio continuity and smoothness',
    'VQScore': 'Overall voice quality assessment',
    'WVMOS': 'Predicted subjective quality rating',
    'SIGMOS_OVRL': 'Comprehensive overall audio quality',
    'SIGMOS_REVERB': 'Perceived reverberation quality'
}

# --- Cached Initializers ---
@st.cache_resource
def init_srmr():
    from metrics.srmr_metric import calculate_srmr
    return calculate_srmr

@st.cache_resource
def init_sigmos():
    from metrics.sigmos_metric import calculate_sigmos, get_estimator
    get_estimator() # Warmup
    return calculate_sigmos

@st.cache_resource
def init_vqscore():
    from metrics.vqscore_metric import calculate_vqscore, load_model
    load_model() # Warmup
    return calculate_vqscore

@st.cache_resource
def init_wvmos():
    from metrics.wvmos_metric import calculate_wvmos, get_model
    get_model() # Warmup
    return calculate_wvmos

# --- Main App Area ---
st.title("🎧 Audio Quality Analytics")
st.markdown("""
Upload an audio file to analyze its quality. 
The system will evaluate it against the **Admin Configured Thresholds** on the left.

💡 **Tip:** Upload a 5-10 minute clip first to validate your recording environment before recording longer sessions.
""")

uploaded_file = st.file_uploader("Choose an audio file", type=['wav'])

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    st.audio(uploaded_file, format='audio/wav')
    
    if st.button("Run Analysis", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        
        try:
            # 0. Initialize Models with Granular Feedback
            with st.status("Initializing AI Models...", expanded=True) as status:
                st.write("Loading SRMR...")
                calculate_srmr = init_srmr()
                
                st.write("Loading SigMOS...")
                calculate_sigmos = init_sigmos()
                
                st.write("Loading VQScore...")
                calculate_vqscore = init_vqscore()
                
                st.write("Loading WVMOS (this is the largest model)...")
                calculate_wvmos = init_wvmos()
                
                status.update(label="All AI Models Loaded & Cached!", state="complete", expanded=False)
                
            # --- Sampling Logic ---
            info = sf.info(tmp_path)
            duration = info.duration
            analysis_paths = []
            
            if duration > 180: # > 3 minutes
                num_chunks = 5
                chunk_duration = 30.0
                st.info(f"Large file detected ({duration/60:.2f} mins). Analyzing {num_chunks} representative clips (30s each) distributed across the file for better coverage.")
                
                # Calculate segment intervals
                segment_length = duration / num_chunks
                
                with st.spinner("Extracting representative samples..."):
                    for i in range(num_chunks):
                        # Center of the segment
                        segment_center = (i * segment_length) + (segment_length / 2)
                        start_time = max(0, segment_center - (chunk_duration / 2))
                        
                        # Boundary checks
                        if start_time + chunk_duration > duration:
                            start_time = max(0, duration - chunk_duration)
                        
                        try:
                            y_clip, sr_clip = librosa.load(tmp_path, sr=None, offset=start_time, duration=chunk_duration)
                            
                            clip_name = f"temp_clip_{i}.wav"
                            clip_path = os.path.join(tempfile.gettempdir(), clip_name)
                            sf.write(clip_path, y_clip, sr_clip)
                            analysis_paths.append(clip_path)
                        except Exception as e:
                            print(f"Error extracting clip {i}: {e}")
                            
                    if not analysis_paths:
                        st.error("Failed to extract samples. Analyzing full file (might be slow).")
                        analysis_paths = [tmp_path]
            else:
                analysis_paths = [tmp_path]
            # ----------------------

            # 1. SRMR
            print("DEBUG: Starting SRMR...")
            status_text.text("Running SRMR...")
            srmr_scores = []
            for path in analysis_paths:
                s = calculate_srmr(path)
                if s is not None: srmr_scores.append(s)
            
            score_srmr = np.mean(srmr_scores) if srmr_scores else 0.0
            print(f"DEBUG: SRMR Finished. Score: {score_srmr}")
            results.append({'Metric': 'SRMR', 'Score': score_srmr})
            progress_bar.progress(25)
            
            # 2. SigMOS
            print("DEBUG: Starting SigMOS...")
            status_text.text("Running SigMOS...")
            sigmos_accumulator = {}
            valid_sigmos_count = 0
            
            for path in analysis_paths:
                scores = calculate_sigmos(path)
                if scores:
                    valid_sigmos_count += 1
                    for k, v in scores.items():
                        sigmos_accumulator[k] = sigmos_accumulator.get(k, 0) + v
                        
            if valid_sigmos_count > 0:
                for k, v in sigmos_accumulator.items():
                    avg_val = v / valid_sigmos_count
                    results.append({'Metric': k, 'Score': avg_val})
            print(f"DEBUG: SigMOS Finished")
            progress_bar.progress(50)
            
            # 3. VQScore
            print("DEBUG: Starting VQScore...")
            status_text.text("Running VQScore...")
            vq_scores = []
            for path in analysis_paths:
                s = calculate_vqscore(path)
                if s is not None: vq_scores.append(s)
                
            score_vq = np.mean(vq_scores) if vq_scores else 0.0
            print(f"DEBUG: VQScore Finished: {score_vq}")
            results.append({'Metric': 'VQScore', 'Score': score_vq})
            progress_bar.progress(75)
            
            # 4. WVMOS
            print("DEBUG: Starting WVMOS...")
            status_text.text("Running WVMOS...")
            wvmos_scores = []
            for path in analysis_paths:
                s = calculate_wvmos(path)
                if s is not None: wvmos_scores.append(s)
                
            score_wvmos = np.mean(wvmos_scores) if wvmos_scores else 0.0
            print(f"DEBUG: WVMOS Finished: {score_wvmos}")
            results.append({'Metric': 'WVMOS', 'Score': score_wvmos})
            
            # 5. Sample Rate Analysis
            print("DEBUG: Starting Sample Rate Analysis...")
            status_text.text("Analyzing Sample Rates...")
            from metrics.samplerate_metric import get_recording_sr, get_mic_sr
            
            # Recording SR: Check ORIGINAL file to see file usage
            rec_sr = get_recording_sr(tmp_path) 
            results.append({'Metric': 'Recording SR', 'Score': rec_sr})
            
            # Mic SR: Check samples (bandwidth analysis)
            mic_sr_scores = []
            for path in analysis_paths:
                s = get_mic_sr(path)
                if s is not None: mic_sr_scores.append(s)
            
            mic_sr = np.mean(mic_sr_scores) if mic_sr_scores else 0
            results.append({'Metric': 'Mic SR', 'Score': mic_sr})
            
            progress_bar.progress(100)
            
            print("DEBUG: Analysis and UI rendering complete.")
            status_text.text("Analysis Complete!")
            
            # Process Results
            final_rows = []
            for item in results:
                metric_name = item['Metric']
                score = item['Score']
                threshold = THRESHOLDS.get(metric_name)
                
                status = "PASS" if score is not None and score >= threshold else "FAIL"
                
                # Add context to description if sampled
                desc_suffix = ""
                if duration > 60 and metric_name != 'Recording SR':
                     desc_suffix = " (Avg of 3 clips)"
                
                final_rows.append({
                    "Metric": metric_name,
                    "Description": METRIC_DESCRIPTIONS.get(metric_name, "") + desc_suffix,
                    "Your Threshold": threshold,
                    "Score": round(score, 3) if score is not None else None,
                    "Result": status
                })
                
            df_results = pd.DataFrame(final_rows)
            
            # Display Summary Metrics
            st.divider()
            col1, col2, col3 = st.columns(3)
            
            pass_count = df_results[df_results['Result'] == 'PASS'].shape[0]
            total_count = df_results.shape[0]
            
            col1.metric("Total Checks", total_count)
            col2.metric("Passed", pass_count)
            col3.metric("Failed", total_count - pass_count)
            
            # Display Detailed Table with Styling
            st.subheader("Detailed Analysis")
            
            def highlight_status(val):
                color = 'green' if val == 'PASS' else 'red'
                return f'color: {color}; font-weight: bold'

            st.dataframe(
                df_results.style.map(highlight_status, subset=['Result']),
                use_container_width=True,
                hide_index=True
            )
            
            # --- Qualitative Feedback Section ---
            failed_rows = df_results[df_results['Result'] == 'FAIL']
            if not failed_rows.empty:
                st.divider()
                st.subheader("🛠️ Recommendations for Improvement")
                for index, row in failed_rows.iterrows():
                    metric = row['Metric']
                    feedback = config.METRIC_FEEDBACK.get(metric, "Check your setup.")
                    
                    with st.expander(f"Fix for {metric} (Score: {row['Score']})", expanded=True):
                        st.markdown(feedback)
            # ------------------------------------
            
            # Download Button
            csv = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Report CSV",
                csv,
                "audio_analysis_report.csv",
                "text/csv",
                key='download-csv'
            )
            
        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
            import traceback
            st.code(traceback.format_exc())
            
        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
