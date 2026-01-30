# Audio Quality Analysis Configuration
# Edit these values to change the pass/fail thresholds for the application.

THRESHOLDS = {
    'SRMR': 8.0,            # Technical measurement of reverberation (Higher is better)
    'SIGMOS_DISC': 4.0,     # Audio continuity and smoothness (1-5)
    'VQScore': 0.67,        # Overall voice quality assessment (0-1)
    'WVMOS': 4.0,           # Predicted subjective quality rating (1-5)
    'SIGMOS_OVRL': 3.0,     # Comprehensive overall audio quality (1-5)
    'SIGMOS_REVERB': 3.5    # Perceived reverberation quality (1-5)
}

METRIC_DESCRIPTIONS = {
    'SRMR': 'Technical measurement of reverberation and room acoustics',
    'SIGMOS_DISC': 'Audio continuity and smoothness',
    'VQScore': 'Overall voice quality assessment',
    'WVMOS': 'Predicted subjective quality rating',
    'SIGMOS_OVRL': 'Comprehensive overall audio quality',
    'SIGMOS_REVERB': 'Perceived reverberation quality'
}
