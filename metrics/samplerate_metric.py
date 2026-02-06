import librosa
import numpy as np
import soundfile as sf

def get_recording_sr(audio_path):
    """
    Returns the metadata sample rate of the file.
    """
    try:
        info = sf.info(audio_path)
        return info.samplerate
    except Exception as e:
        print(f"Error getting recording SR: {e}")
        return 0

def get_mic_sr(audio_path):
    """
    Estimates the 'Mic Sampling Rate' (Effective Sample Rate) based on bandwidth.
    Calculates the 99% power roll-off frequency and multiplies by 2.
    """
    try:
        # Load with high SR to capture full bandwidth (native sr)
        y, sr = librosa.load(audio_path, sr=None)
        
        # Compute magnitude spectrum
        S_full, phase = librosa.magphase(librosa.stft(y))
        
        # Max Hold Spectrum (Peak detection across time)
        # Instead of average, we take the MAX magnitude at each frequency bin across all time frames.
        # This aligns with "Max peaks on the spectrogram".
        S_max = np.max(S_full, axis=1)
        
        # Normalize to Max Peak (0 Reference)
        S_ref = np.max(S_max)
        if S_ref == 0:
            return 0
            
        # Convert to dB relative to peak
        S_db = librosa.amplitude_to_db(S_max, ref=S_ref)
        
        # Threshold: Find the highest frequency that is within X dB of the peak.
        # Typical noise floor might be -80dB or -90dB.
        # We look for the "last" bin that is ABOVE the threshold.
        threshold_db = -80.0
        
        fft_freqs = librosa.fft_frequencies(sr=sr)
        
        # Find indices where signal > threshold
        valid_indices = np.where(S_db > threshold_db)[0]
        
        if len(valid_indices) == 0:
            return 0
            
        # The highest index with significant energy
        last_idx = valid_indices[-1]
        cutoff_freq = fft_freqs[last_idx]
        
        # Effective SR is 2 * Cutoff
        effective_sr = int(cutoff_freq * 2)
        
        return effective_sr
    except Exception as e:
        print(f"Error calculating Mic SR: {e}")
        return 0
