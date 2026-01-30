from wvmos import get_wvmos

_wvmos_model = None

def get_model():
    global _wvmos_model
    if _wvmos_model is None:
        # cuda=False for compatibility, or check availability
        import torch
        cuda = torch.cuda.is_available()
        _wvmos_model = get_wvmos(cuda=cuda)
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
        return None
