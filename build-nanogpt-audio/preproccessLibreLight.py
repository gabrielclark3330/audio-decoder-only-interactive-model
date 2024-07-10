import os
import shutil
from pydub import AudioSegment
import subprocess
from tqdm import tqdm

def find_flac_files(dataset_folder):
    flac_files = []
    for root, _, files in os.walk(dataset_folder):
        for file in files:
            if file.endswith('.flac'):
                flac_files.append(os.path.join(root, file))
    return flac_files

def copy_flac_files(flac_files, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    for file in flac_files:
        shutil.copy(file, destination_folder)

def convert_to_mp3(destination_folder, sample_rate=24000):
    for file in tqdm(os.listdir(destination_folder)):
        if file.endswith('.flac'):
            flac_path = os.path.join(destination_folder, file)
            mp3_path = os.path.join(destination_folder, os.path.splitext(file)[0] + '.mp3')
            # Use ffmpeg to convert the file
            subprocess.run([
                'ffmpeg', '-y', '-i', flac_path, '-ar', str(sample_rate), '-ac', '2', '-b:a', '192k', mp3_path
            ], check=True)
            os.remove(flac_path)  # Remove the original flac file after conversion


dataset_folder = '../smalllibralight/'
output_folder = os.path.join(os.path.dirname(dataset_folder), 'flac_to_mp3_output')

# Step 1: Find all flac files
#flac_files = find_flac_files(dataset_folder)
print("found files")

# Step 2: Copy all flac files to the new folder
#copy_flac_files(flac_files, output_folder)
print("converting files")

# Step 3: Convert all flac files in the new folder to mp3 with 24kHz sampling rate
convert_to_mp3(output_folder)