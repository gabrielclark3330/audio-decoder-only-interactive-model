import torch
import torchaudio
from speech_tokenizer import SpeechTokenizer
import numpy as np
from tqdm import tqdm
import itertools
from pathlib import Path
import os

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

tokenizer = SpeechTokenizer(device=device)

seconds_per_batch = 3
batch_size = 8
print("batch size:", batch_size)

def resample_waveform(waveform, sample_rate, new_sample_rate, chunk_size=10000000):
    resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=new_sample_rate)
    resampled_waveform = []

    for start in range(0, waveform.size(1), chunk_size):
        end = min(start + chunk_size, waveform.size(1))
        chunk = waveform[:, start:end]
        resampled_chunk = resampler(chunk)
        resampled_waveform.append(resampled_chunk)

    return torch.cat(resampled_waveform, dim=1)

data_path = "../audiodata"
file_ext = 'mp3'

for root, dirs, files in os.walk(data_path):
    relative_root = os.path.relpath(root, data_path)
    out_dir = Path(data_path).parent / "build-nanogpt-audio" / "data" / f"{Path(relative_root).name}_npy"
    #if os.path.isdir(out_dir):
        #continue
    out_dir.mkdir(parents=True, exist_ok=True)

    already_created_files = os.listdir(out_dir)

    for file in files:
        if file.endswith(file_ext):
            audio_path = os.path.join(root, file)
            output_file = f"{out_dir}/{Path(file).stem}.npy"
            if os.path.exists(output_file):
                print(f"Skipping {audio_path}, already processed.")
                continue
            print("processing: ", audio_path)
            waves = []
            waveform, sample_rate = torchaudio.load(audio_path, backend='soundfile')
            print("loaded")
            # Resample to 24kHz if necessary
            if sample_rate != tokenizer.sample_rate:
                waveform = resample_waveform(waveform, sample_rate, tokenizer.sample_rate)
            print("sampled")
            # Convert to mono by averaging the channels if the audio is stereo
            if waveform.size(0) > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            i = 0
            while 10*(i+1)*tokenizer.sample_rate < waveform.shape[-1]:
                waves.append(waveform[:, tokenizer.sample_rate*seconds_per_batch*i : tokenizer.sample_rate*seconds_per_batch*(i+1)])
                i += 1
            print("waved")
            waves.append(waveform[:, tokenizer.sample_rate*seconds_per_batch*i : ])
            batches = list(batch_list(waves, batch_size))
            print("running model for batches")
            single_doc = []
            for batch in tqdm(batches[:-1]):
                encoded_batch = tokenizer.encode(batch)
                for x in encoded_batch:
                    single_doc.extend(x[:-1])
            
            np.save(output_file, single_doc)
            print(f"saved {output_file} len {len(single_doc)}")
