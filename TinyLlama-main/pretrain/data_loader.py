import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import os
import random
import time

class NumpyAudioDataset(Dataset):
    def __init__(self, file_paths, block_size, process_rank, num_processes):
        self.file_paths = file_paths
        self.block_size = block_size
        self.process_rank = process_rank
        self.num_processes = num_processes
        self.file_block_counts = [np.load(file_path).shape[0]-self.block_size for file_path in self.file_paths]
        self.data_indices = np.cumsum(self.file_block_counts)

    def _find_file_index(self, idx):
        file_idx = np.searchsorted(self.data_indices, idx, side='right')
        return file_idx

    def _load_tokens(self, idx):
        file_idx = self._find_file_index(idx)
        filename = self.file_paths[file_idx]
        npt = np.load(filename)
        npt = npt.astype(np.int32)
        if file_idx == 0:
            relative_idx = idx
        else:
            relative_idx = idx - self.data_indices[file_idx - 1]

        ptt = torch.tensor(npt[relative_idx:relative_idx+self.block_size+1], dtype=torch.long)
        return ptt

    def __len__(self):
        return self.data_indices[-1]

    def __getitem__(self, idx):
        tokens = self._load_tokens(idx)
        x = tokens[:-1]  # inputs
        y = tokens[1:]   # targets
        return x, y

# Example usage:
data_root = "../../build-nanogpt-audio/data"
shards = [] #[x for x in os.listdir(data_root)]
for entry in os.listdir(data_root):
    full_path = os.path.join(data_root, entry)
    for nested_entry in os.listdir(full_path):
        shards.append(os.path.join(full_path, nested_entry))
shards.sort()
train_file_paths = shards[:int(len(shards)*0.9)]
val_file_paths = shards[int(len(shards)*0.9):]
random.shuffle(train_file_paths)
random.shuffle(val_file_paths)

dataset = NumpyAudioDataset(val_file_paths, block_size=32, process_rank=0, num_processes=1)
dataloader = DataLoader(dataset, batch_size=2, shuffle=True, prefetch_factor=None)

# Test the dataloader
'''
iter = 0
start = time.time()
for out in dataloader:
    #print(time.time()-start)
    print(out)
    start = time.time()
    iter += 1
    if iter == 2:
        break
'''

