import os
import numpy as np
import soundfile as sf
import librosa
# Import SigMOS from the local copy
from metrics.sigmos.sigmos import SigMOS

# Initialize the estimator once to avoid reloading model
_sigmos_estimator = None

def get_estimator():
    global _sigmos_estimator
    if _sigmos_estimator is None:
        model_dir = os.path.join(os.path.dirname(__file__), 'sigmos')
        _sigmos_estimator = SigMOS(model_dir=model_dir)
    return _sigmos_estimator

def calculate_sigmos(audio_path):
    """
    Calculates SIGMOS scores.
    Returns a dictionary with SIGMOS_DISC, SIGMOS_OVRL, SIGMOS_REVERB.
    Thresholds:
    - DISC: >= 4.0
    - OVRL: >= 3.0
    - REVERB: >= 3.5
    """
    try:
        estimator = get_estimator()
        
        # Load audio
        # SigMOS expects 48kHz. The run method handles resampling if sr is provided.
        y, fs = sf.read(audio_path)
        
        if len(y.shape) > 1:
            y = y[:, 0]
            
        result = estimator.run(y, sr=fs)
        
        return {
            'SIGMOS_DISC': result['MOS_DISC'],
            'SIGMOS_OVRL': result['MOS_OVRL'],
            'SIGMOS_REVERB': result['MOS_REVERB']
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error calculating SIGMOS for {audio_path}: {e}")
        return None
