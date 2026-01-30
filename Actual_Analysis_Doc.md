TTS DATA - AUDIO QUALITY
EVALUATION CRITERIA
This document outlines the minimum audio quality standards required for all audio data
submissions. All audio files must meet or exceed the thresholds specified below to be
accepted. These evaluations should be run at the individual segment level.
QUALITY METRICS AND THRESHOLDS
The following six metrics will be used to evaluate audio quality. All thresholds must be met
simultaneously for an audio file to pass quality control:
1. SRMR (Speech-to-Reverberation Modulation Energy Ratio)
Threshold: ≥ 8.0
What it measures: Technical measurement of reverberation and room acoustics
●
●
●
●
Higher values indicate cleaner audio with less reverberation
Assesses the impact of room acoustics on speech intelligibility
Critical for ensuring audio is recorded in appropriate acoustic environments
Github: https://github.com/shimhz/SRMRpy
2. SIGMOS
_
DISC (Discontinuity)
Threshold: ≥ 4.0
What it measures: Audio continuity and smoothness
●
●
●
●
Detects clicks, pops, dropouts, and other discontinuities
Scale: 1 (poor) to 5 (excellent)
Ensures audio is free from technical artifacts and interruptions
Github: https://github.com/microsoft/SIG-Challenge/tree/main/ICASSP2024/sigmos
3. vqscore (Voice Quality Score)
Threshold: ≥ 0.67
What it measures: Overall voice quality assessment
●
●
●
●
Evaluates naturalness and clarity of speech
Scale: 0 (poor) to ~0.81 (excellent)
Ensures high-quality voice characteristics
GIthub: https://github.com/JasonSWFu/VQscore
4. wvmos (WaveMOS - Mean Opinion Score)
Threshold: ≥ 4.0
What it measures: Predicted subjective quality rating
●
●
●
●
Simulates human perception of audio quality
Scale: 1 (bad) to 5 (excellent)
Correlates with how listeners would rate the audio
Github: https://github.com/AndreevP/wvmos
5. SIGMOS
_
OVRL (Overall Quality)
Threshold: ≥ 3.0
What it measures: Comprehensive overall audio quality
●
●
●
●
Holistic assessment of audio quality
Scale: 1 (poor) to 5 (excellent)
Catches quality issues that may not be captured by individual metrics
Github: Same as SIGMOS
DISC
_
6. SIGMOS
_
REVERB (Reverberation - Perceptual)
Threshold: ≥ 3.5
What it measures: Perceived reverberation quality
●
●
●
●
Subjective assessment of reverb and echo
Scale: 1 (poor) to 5 (excellent)
Complements technical SRMR measurement with perceptual validation
Github: Same as SIGMOS
DISC
_
QUALITY CONTROL PROCESS
Evaluation Method
All submitted audio files will be automatically processed through these six metrics. Files
must meet ALL six thresholds to pass quality control. Results will be provided in a detailed
report showing scores for each metric.
Pass/Fail Criteria
✓ PASS: All six metrics meet or exceed their respective thresholds
✗ FAIL: One or more metrics fall below threshold
RECORDING BEST PRACTICES
To ensure audio meets these thresholds:
Environment
●
●
●
Record in quiet, acoustically treated spaces
Minimize background noise and echo
Avoid outdoor or reverberant locations
Equipment
●
●
●
Use professional-grade microphones
Maintain proper microphone distance (6-12 inches typically)
Ensure all connections are secure and high-quality
Technical Setup
●
●
●
Use appropriate sample rate (minimum 16 kHz, recommended 44.1+ kHz)
Set proper gain levels to avoid clipping or excessive noise floor
Monitor audio quality during recording
Post-Processing
●
●
●
Avoid aggressive compression or noise reduction that may introduce artifacts
Maintain natural voice characteristics
Ensure consistent volume levels
SUBMISSION REQUIREMENTS
●
●
●
●
Test sample files against all six metrics
Verify all thresholds are met
Document recording environment and equipment used
Include metadata (sample rate, bit depth, recording conditions)