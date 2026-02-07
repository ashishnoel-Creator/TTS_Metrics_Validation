from wvmos import get_wvmos
import streamlit as st

_wvmos_model = None

def get_model():
    global _wvmos_model
    if _wvmos_model is None:
        # Auto-detect device (MPS for Mac, CUDA for NVIDIA, CPU otherwise)
        import torch
        if torch.backends.mps.is_available():
            device = 'mps'
        elif torch.cuda.is_available():
            device = 'cuda'
        else:
            device = 'cpu'
            
        print(f"Loading WVMOS model on {device}...")
        _wvmos_model = get_wvmos(device=device)
    return _wvmos_model

def calculate_wvmos(audio_path):
    """
    Calculates WVMOS score.
    Threshold: >= 4.0
    """
    try:
        model = get_model()
        score = model.calculate_one(audio_path)
        return score
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error calculating WVMOS for {audio_path}: {e}")
        st.error(f"WVMOS Error: {e}")
        return None
