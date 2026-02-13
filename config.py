# Audio Quality Analysis Configuration
# Edit these values to change the pass/fail thresholds for the application.

THRESHOLDS = {
    'SRMR': 6.0,            # Technical measurement of reverberation (Higher is better)
    'SIGMOS_DISC': 3.5,     # Audio continuity and smoothness (1-5)
    'VQScore': 0.65,        # Overall voice quality assessment (0-1)
    'WVMOS': 1.5,           # Predicted subjective quality rating (1-5)
    'SIGMOS_OVRL': 2.8,     # Comprehensive overall audio quality (1-5)
    'SIGMOS_REVERB': 3.5,   # Perceived reverberation quality (1-5)
    'Recording SR': 44100,  # File metadata sample rate (Hz)
    'Mic SR': 16000         # Effective captured bandwidth (Hz)
}

GIT_VERSION = "5ea5b92"

METRIC_DESCRIPTIONS = {
    'SRMR': 'Technical measurement of reverberation and room acoustics',
    'SIGMOS_DISC': 'Audio continuity and smoothness',
    'VQScore': 'Overall voice quality assessment',
    'WVMOS': 'Predicted subjective quality rating',
    'SIGMOS_OVRL': 'Comprehensive overall audio quality',
    'SIGMOS_REVERB': 'Perceived reverberation quality',
    'Recording SR': 'Digital Sampling Rate of the file (should be >= 44.1kHz)',
    'Mic SR': 'Estimated effective bandwidth of the microphone (should conform to > 16kHz capture)'
}

METRIC_FEEDBACK = {
    'SRMR': "The audio has high reverberation or room echo. \n**Fix:** Record in a smaller room, use sound-absorbing materials (curtains, foam), or get closer to the mic.",
    'SIGMOS_DISC': "The audio sounds choppy or has interruptions. \n**Fix:** Check your internet connection (if VoIP), reduce CPU load, or check for faulty cables.",
    'VQScore': "The voice quality is degraded (robotic, fuzzy). \n**Fix:** Use a higher quality microphone, check for codec compression issues, or increase bitrate.",
    'WVMOS': "The overall subjective quality is low. \n**Fix:** This is a comprehensive score. Check for background noise, bad mic, or aggressive compression. Try recording a cleaner sample.",
    'SIGMOS_OVRL': "The overall signal quality is poor. \n**Fix:** Ensure a quiet environment and a decent microphone. Avoid post-processing that introduces artifacts.",
    'SIGMOS_REVERB': "Too much echo detected. \n**Fix:** Treat your room acoustics or move the microphone away from reflective surfaces (walls, windows).",
    'Recording SR': "The file quality is low (Sample Rate < 44.1kHz). \n**Fix:** Check your recording software settings and ensure it's set to 44.1kHz or 48kHz.",
    'Mic SR': "The microphone is not capturing the full frequency range (Low Bandwidth). \n**Fix:** You might be using a low-quality mic (e.g., Bluetooth headset) or a high-cut filter is active. Use a better mic or check filters."
}
