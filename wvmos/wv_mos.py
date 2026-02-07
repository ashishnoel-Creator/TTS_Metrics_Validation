from transformers import Wav2Vec2Model, Wav2Vec2Processor
import torch    
from collections import OrderedDict
import glob
import librosa
import tqdm
import numpy as np
from torch import nn

def extract_prefix(prefix, weights):
    result = OrderedDict()
    for key in weights:
        if key.find(prefix) == 0:
            result[key[len(prefix):]] = weights[key]
    return result     


class Wav2Vec2ConvEncoder:

    def __init__(self, device="cuda"):
        self.encoder = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base").feature_extractor
        self.encoder.eval()
        self.encoder = self.encoder.to(device)
        self.preprocessor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
        self.preprocessor._sample_rate = 16000
        self.device = device

    def __call__(self, x):
        # x - [bs, 1, time]
        x = x[:, 0]
        input_values = (x - x.mean(-1)[:, None]) / (x.std(-1)[:, None] + 1e-6)
        hidden_states = self.encoder(input_values.to(self.device))
        return hidden_states
    
class Wav2Vec2FullEncoder:

    def __init__(self, device="cuda"):
        self.encoder = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base")
        self.encoder.eval()
        self.encoder = self.encoder.to(device)
        self.preprocessor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
        self.preprocessor._sample_rate = 16000
        self.device = device

    def __call__(self, x):
        # x - [bs, 1, time]
        x = x[:, 0]
        input_values = (x - x.mean(-1)[:, None]) / (x.std(-1)[:, None] + 1e-6)
        hidden_states = self.encoder(input_values.to(self.device)).last_hidden_state
        return hidden_states.transpose(-2, -1)
    
    
class Wav2Vec2MOS(nn.Module):
    def __init__(self, path, freeze=True, cuda=True, device=None):
        super().__init__()
        self.encoder = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base")
        self.freeze = freeze
        
        self.dense = nn.Sequential(
            nn.Linear(768, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 1)
        )
        
        if self.freeze:
            self.encoder.eval()
            for p in self.encoder.parameters():
                p.requires_grad_(False)
        
        # PyTorch 2.6+ defaults to weights_only=True, which blocks older checkpoints with custom globals.
        # We set weights_only=False to allow loading the Zenodo-hosted checkpoint.
        checkpoint_data = torch.load(path, map_location='cpu', weights_only=False)
        self.load_state_dict(extract_prefix('model.', checkpoint_data['state_dict']))
        self.eval()
        
        if device is not None:
            self.device = torch.device(device)
        elif cuda and torch.cuda.is_available():
            self.device = torch.device('cuda')
        else:
            self.device = torch.device('cpu')
            
        self.to(self.device)
        self.processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
        
    def forward(self, x):
        x = self.encoder(x)['last_hidden_state'] # [Batch, time, feats]
        x = self.dense(x) # [batch, time, 1]
        x = x.mean(dim=[1,2], keepdims=True) # [batch, 1, 1]
        return x
                
    def train(self, mode):
        super().train(mode)
        if self.freeze:
            self.encoder.eval()
            
    def calculate_dir(self, path, mean=True):
        
        pred_mos = []
        for path in tqdm.tqdm(sorted(glob.glob(f"{path}/*.wav"))):
            signal = librosa.load(path, sr=16_000)[0]
            x = self.processor(signal, return_tensors="pt", padding=True, sampling_rate=16000).input_values
            x = x.to(self.device)
            with torch.no_grad():
                res = self.forward(x).mean()
            pred_mos.append(res.item())
        if mean:
            return np.mean(pred_mos)
        else:
            return pred_mos
        
    def calculate_one(self, path):
        # 1. Load Audio (Original 16k)
        signal = librosa.load(path, sr=16_000)[0]
        
        # 2. Sliding Window (5-minute window, 2.5-minute overlap)
        # 600s (10-min) caused runtime failures/OOM on Hugging Face.
        # 300s (5-min) was verified to have 0.09 deviation (within 0.1 tolerance)
        # and is much safer for memory.
        window_size = 16000 * 300  # 5 minutes
        stride = 16000 * 150       # 2.5 minutes
        
        # Prepare windows
        chunks = []
        if len(signal) <= window_size:
            chunks.append(signal)
        else:
            for i in range(0, len(signal), stride):
                chunk = signal[i : i + window_size]
                if len(chunk) < 16000: 
                    continue
                chunks.append(chunk)

        weighted_scores = 0.0
        total_weight = 0.0
        
        for chunk in chunks:
            # Score EVERYTHING (including silence) to match "Whole File" accuracy.
            x = self.processor(chunk, return_tensors="pt", padding=True, sampling_rate=16000).input_values
            with torch.no_grad():
                x = x.to(self.device)
                val = self.forward(x).mean().cpu().item()
                
                # Weight by length
                current_len = len(chunk)
                weighted_scores += val * current_len
                total_weight += current_len
        
        if total_weight == 0:
            return 0.0
            
        return weighted_scores / total_weight