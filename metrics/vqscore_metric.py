import os
import sys
import yaml
import torch
import torchaudio
import numpy as np

# Add metrics directory to sys.path to allow importing vqscore_models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metrics.vqscore_models.VQVAE_models import VQVAE_QE

_vqscore_model = None
_vqscore_config = None
_device = None

def stft_magnitude(x, hop_size, fft_size=512, win_length=512):
    window = torch.hann_window(win_length).to(x.device)
        
    x_stft = torch.stft(
        x, fft_size, hop_size, win_length, window=window, return_complex=False
    )
    real = x_stft[..., 0]
    imag = x_stft[..., 1]
    
    return torch.sqrt(torch.clamp(real ** 2 + imag ** 2, min=1e-7)).transpose(2, 1)

def cos_loss(SP_noisy, SP_y_noisy):  
    eps=1e-5
    SP_noisy_norm = torch.norm(SP_noisy, p=2, dim=-1, keepdim=True)+eps
    SP_y_noisy_norm = torch.norm(SP_y_noisy, p=2, dim=-1, keepdim=True)+eps  
    Cos_frame = torch.sum(SP_noisy/SP_noisy_norm * SP_y_noisy/SP_y_noisy_norm, dim=-1) 
    return -torch.mean(Cos_frame)

def load_model():
    global _vqscore_model, _vqscore_config, _device
    if _vqscore_model is not None:
        return
    
    base_dir = os.path.dirname(__file__)
    config_path = os.path.join(base_dir, 'vqscore_config', 'QE_cbook_size_2048_1_32_IN_input_encoder_z_Librispeech_clean_github.yaml')
    
    # Find the checkpoint file
    exp_dir = os.path.join(base_dir, 'vqscore_exp', 'QE_cbook_size_2048_1_32_IN_input_encoder_z_Librispeech_clean_github')
    checkpoint_path = os.path.join(exp_dir, 'checkpoint-dnsmos_ovr_CC=0.835.pkl')
    
    with open(config_path, 'r') as f:
        _vqscore_config = yaml.load(f, Loader=yaml.FullLoader)
        
    if torch.backends.mps.is_available():
        _device = torch.device('mps')
    elif torch.cuda.is_available():
        _device = torch.device('cuda')
    else:
        _device = torch.device('cpu')
        
    print(f"Loading VQScore model on {_device}...")
    _vqscore_model = VQVAE_QE(**_vqscore_config['VQVAE_params']).to(_device).eval()
    
    # Load weights
    # The checkpoint seems to be a full pickle or state dict?
    # inference.py says: VQVAE.load_state_dict(torch.load(args.path_of_model_weights)['model']['VQVAE'])
    checkpoint = torch.load(checkpoint_path, map_location=_device)
    _vqscore_model.load_state_dict(checkpoint['model']['VQVAE'])

def calculate_vqscore(audio_path):
    """
    Calculates VQScore.
    Threshold: >= 0.67
    """
    try:
        load_model()
        
        hop_size = 256
        # Use librosa for robust loading on Cloud (avoids torchaudio backend issues)
        import librosa
        wav_input, fs = librosa.load(audio_path, sr=None, mono=False)
        wav_input = torch.from_numpy(wav_input)
        
        # Ensure (C, T) shape
        if wav_input.ndim == 1:
            wav_input = wav_input.unsqueeze(0)
            
        # VQScore expects 16k
        if fs != 16000:
            resampler = torchaudio.transforms.Resample(fs, 16000)
            wav_input = resampler(wav_input)
            
        wav_input = wav_input.to(_device)
        SP_input = stft_magnitude(wav_input, hop_size=hop_size)
        
        if _vqscore_config['input_transform'] == 'log1p':
            SP_input = torch.log1p(SP_input)
            
        with torch.no_grad():
            z = _vqscore_model.CNN_1D_encoder(SP_input)
            zq, indices, vqloss, distance = _vqscore_model.quantizer(z, stochastic=False, update=False)
            
            # VQScore is calculated as negative cos loss between z and zq?
            # inference.py: VQScore_cos_z = -cos_loss(z.transpose(2, 1).cpu(), zq.cpu()).numpy()
            
            score = -cos_loss(z.transpose(2, 1).cpu(), zq.cpu()).item()
            
        return score
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error calculating VQScore for {audio_path}: {e}")
        return None
