import torch, torchaudio
from speech_tokenizer import SpeechTokenizer
import numpy as np
from tqdm import tqdm
import itertools
from pathlib import Path
import os
#snapshot_download(repo_id="eastwind/tiny-sherlock-audio", local_dir='./tiny-sherlock-audio', repo_type='dataset')

def is_file_done_processing(file, list_of_files):
    for target_file in list_of_files:
        if file in target_file:
            return True
    return False

device = "cpu"
if torch.cuda.is_available():
    device = "cuda"
elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
    device = "mps"
print(f"using device: {device}")

def batch_list(lst, batch_size):
    it = iter(lst)
    return iter(lambda: list(itertools.islice(it, batch_size)), [])

out_path = './data'
Path(out_path).mkdir(parents=True, exist_ok=True)

tokenizer = SpeechTokenizer(device=device)

seconds_per_batch = 3
batch_size = 2
print("batch size:", batch_size)

already_created_files = os.listdir(out_path)

data_path = "../nanoGPT-master/data/lexaudio/lexscrape"
file_ext = 'mp3'

def resample_waveform(waveform, sample_rate, new_sample_rate, chunk_size=10000000):
    resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=new_sample_rate)
    resampled_waveform = []

    for start in range(0, waveform.size(1), chunk_size):
        end = min(start + chunk_size, waveform.size(1))
        chunk = waveform[:, start:end]
        resampled_chunk = resampler(chunk)
        resampled_waveform.append(resampled_chunk)

    return torch.cat(resampled_waveform, dim=1)

for audio_path in sorted([x for x in os.listdir(data_path) if file_ext in x]):
    if is_file_done_processing(audio_path, already_created_files):
        continue
    print("processing: ", audio_path)
    waves = []
    waveform, sample_rate = torchaudio.load(f'{data_path}/{audio_path}', backend='soundfile')
    print("loaded")
    # Resample to 24kHz if necessary
    if sample_rate != tokenizer.sample_rate:
        #resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=tokenizer.sample_rate)
        #waveform = resampler(waveform)
        waveform = resample_waveform(waveform, sample_rate, tokenizer.sample_rate)
    print("sampled")
    # Convert to mono by averaging the channels if the audio is stereo
    if waveform.size(0) > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)
    i = 0
    while 10*(i+1)*tokenizer.sample_rate < waveform.shape[-1]:
        waves.append(waveform[:, tokenizer.sample_rate*seconds_per_batch*i : tokenizer.sample_rate*seconds_per_batch*(i+1)])
        i+=1
    print("waved")
    waves.append(waveform[:, tokenizer.sample_rate*seconds_per_batch*i : ])
    batches = list(batch_list(waves, batch_size))
    # batches = batch_list(waves, batch_size)
    print("running model for batches")
    single_doc = []
    for batch in tqdm(batches[:-1]):
        encoded_batch = tokenizer.encode(batch)
        for x in encoded_batch:
            single_doc.extend(x[:-1])
    
    np.save(f"{out_path}/lex_{audio_path}", single_doc)