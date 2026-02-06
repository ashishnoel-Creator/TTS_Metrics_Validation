import torch
import librosa
import numpy as np
from wvmos import get_wvmos
import warnings
warnings.filterwarnings("ignore")

# Load Model
print("Loading model...")
model = get_wvmos(cuda=False) # Use CPU for consistency
audio_path = "New Audio/Tariq_V1/JAM&JAYPROJECT2.wav"

def score_tensor(model, tensor):
    with torch.no_grad():
        res = model.forward(tensor).mean().item()
    return res

def calc_ground_truth(path):
    print("\n[1] Calculating Ground Truth (Whole File)...")
    try:
        signal = librosa.load(path, sr=16_000)[0]
        x = model.processor(signal, return_tensors="pt", padding=True, sampling_rate=16000).input_values
        score = score_tensor(model, x)
        print(f" -> Score: {score:.4f}")
        return score
    except Exception as e:
        print(f" -> Failed (OOM?): {e}")
        return None

def calc_current_window(path, window=30, stride=15, skip_silence=True):
    print(f"\n[2] Calculating Windowed (Win={window}s, Stride={stride}s, SkipSilence={skip_silence})...")
    signal = librosa.load(path, sr=16_000)[0]
    
    window_samples = 16000 * window
    stride_samples = 16000 * stride
    
    chunks = []
    if len(signal) <= window_samples:
        chunks.append(signal)
    else:
        for i in range(0, len(signal), stride_samples):
            chunk = signal[i : i + window_samples]
            if len(chunk) < 16000: continue
            chunks.append(chunk)
            
    scores = []
    weights = []
    
    for chunk in chunks:
        if skip_silence:
            intervals = librosa.effects.split(chunk, top_db=40)
            if len(intervals) == 0: continue
            
        x = model.processor(chunk, return_tensors="pt", padding=True, sampling_rate=16000).input_values
        val = score_tensor(model, x)
        scores.append(val)
        weights.append(len(chunk))
        
    if not scores: return 0.0
    final = np.average(scores, weights=weights)
    print(f" -> Score: {final:.4f}")
    return final

def calc_concat_silence_removed(path, window=30):
    print(f"\n[3] Calculating Concat-Silence-Removed (Win={window}s)...")
    signal = librosa.load(path, sr=16_000)[0]
    intervals = librosa.effects.split(signal, top_db=30)
    
    if len(intervals) > 0:
        signal = np.concatenate([signal[s:e] for s, e in intervals])
    
    # Then chunk the CLEAN signal
    chunk_samples = 16000 * window
    chunks = [signal[i:i + chunk_samples] for i in range(0, len(signal), chunk_samples)]
    
    scores = []
    weights = []
    for chunk in chunks:
        if len(chunk) < 16000: continue
        x = model.processor(chunk, return_tensors="pt", padding=True, sampling_rate=16000).input_values
        val = score_tensor(model, x)
        scores.append(val)
        weights.append(len(chunk))
        
    if not scores: return 0.0
    final = np.average(scores, weights=weights)
    print(f" -> Score: {final:.4f}")
    return final

def calc_trimmed(path, window=30, stride=30, trim_sec=2):
    print(f"\n[4] Calculating Trimmed (Win={window}s, Trim={trim_sec}s)...")
    signal = librosa.load(path, sr=16_000)[0]
    
    chunk_samples = 16000 * window
    trim_samples = 16000 * trim_sec
    
    # Simple non-overlapping chunks for this test (Sequence logic) or Stride?
    # Let's use simple chunks and see if trimming the START helps.
    chunks = []
    for i in range(0, len(signal), chunk_samples):
        chunk = signal[i : i + chunk_samples]
        if len(chunk) < 16000: continue
        chunks.append(chunk)
        
    all_scores = []
    
    for i, chunk in enumerate(chunks):
        x = model.processor(chunk, return_tensors="pt", padding=True, sampling_rate=16000).input_values
        with torch.no_grad():
            # Manual Forward to get sequence
            out = model.encoder(x)['last_hidden_state']
            dense = model.dense(out) # [1, time, 1]
            
            # Trim padding artifact?
            # Wav2Vec2 output rate is approx 50Hz (20ms stride).
            # 16000 samples -> ~320 samples -> ~500 frames.
            # 2s trim -> ~100 frames.
            
            seq = dense.squeeze() # [time]
            
            # Trim Start
            if i > 0: # Don't trim start of file
                seq = seq[int(50*trim_sec):]
            
            # Trim End? (Maybe not needed if purely sequential)
            # Let's just trim start for now (Warmup artifact)
            
            all_scores.append(seq)
            
    if not all_scores: return 0.0
    full = torch.cat(all_scores)
    final = full.mean().item()
    print(f" -> Score: {final:.4f}")
    return final

# Execution
try:
    gt = calc_ground_truth(audio_path)
    
    # 60s
    win60 = calc_current_window(audio_path, window=60, stride=30, skip_silence=False)
    
    # 300s (5 mins)
    win300 = calc_current_window(audio_path, window=300, stride=150, skip_silence=False)

    # 600s (10 mins) - The "Big Chunk" hypothesis
    win600 = calc_current_window(audio_path, window=600, stride=300, skip_silence=False)
    
    print("\n--- SUMMARY ---")
    if gt: 
        print(f"Ground Truth:         {gt:.4f}")
        print(f"Win 60s:              {win60:.4f} (Diff: {win60-gt:.4f})")
        print(f"Win 300s:             {win300:.4f} (Diff: {win300-gt:.4f})")
        print(f"Win 600s:             {win600:.4f} (Diff: {win600-gt:.4f})")
        
        # Check if any meets tolerance 0.15
        for name, val in [("Win300", win300), ("Win600", win600)]:
            diff = abs(val - gt)
            if diff <= 0.15:
                print(f"✅ SUCCESS: {name} is within tolerance. Diff: {diff:.4f}")

except Exception as e:
    import traceback
    traceback.print_exc()
