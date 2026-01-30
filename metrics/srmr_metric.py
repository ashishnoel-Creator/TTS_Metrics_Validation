import numpy as np
import soundfile as sf
from srmrpy.srmr import srmr

def calculate_srmr(audio_path):
    """
    Calculates SRMR score for the given audio file.
    Threshold: >= 8.0
    """
    try:
        y, fs = sf.read(audio_path)
        
        # Handle multi-channel audio by taking the first channel
        if len(y.shape) > 1:
            y = y[:, 0]
        
        # Ensure float and normalize if integer
        if np.issubdtype(y.dtype, np.integer):
            y = y.astype('float') / np.iinfo(y.dtype).max

        # Resample to 16kHz for SRMR (standard for threshold 8.0)
        TARGET_SR = 16000
        if fs != TARGET_SR:
            import librosa
            y = librosa.resample(y, orig_sr=fs, target_sr=TARGET_SR)
            fs = TARGET_SR
            
        score = srmr(y, fs)
        return float(score)
    except Exception as e:
        print(f"Error calculating SRMR for {audio_path}: {e}")
        return None
