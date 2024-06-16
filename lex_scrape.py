'''
import os
from pytube import Playlist, YouTube
from pydub import AudioSegment

# Function to download and convert a YouTube video to MP3
def download_video_as_mp3(video_url, output_path, max_size=4 * 1024 * 1024 * 1024):
    try:
        yt = YouTube(video_url)
        # Get the audio stream with the highest bitrate
        audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
        for audio_stream in audio_streams:
            if audio_stream.filesize < max_size:
                output_file = audio_stream.download(output_path)
                # Convert to MP3
                base, ext = os.path.splitext(output_file)
                mp3_file = base + '.mp3'
                AudioSegment.from_file(output_file).export(mp3_file, format='mp3')
                os.remove(output_file)
                print(f"Downloaded and converted: {yt.title}")
                break
        else:
            print(f"Error: No suitable audio stream found for {video_url}")
    except Exception as e:
        print(f"Error downloading {video_url}: {e}")

# Function to download all videos in a playlist as MP3
def download_playlist_as_mp3(playlist_url, output_path, max_size=4 * 1024 * 1024 * 1024):
    playlist = Playlist(playlist_url)
    for video_url in playlist.video_urls:
        download_video_as_mp3(video_url, output_path, max_size)

# Replace with your playlist URL and output path
playlist_url = 'ttps://www.youtube.com/playlist?list=PLrAXtmErZgOdP_8GztsuKi9nrraNbKKp4'
output_path = './lexscrape'

if not os.path.exists(output_path):
    os.makedirs(output_path)

download_playlist_as_mp3(playlist_url, output_path)
'''

import os
import subprocess

# Path to the nohup.out file
nohup_file_path = './nohup.out'

# Path to the cookies file
cookies_file_path = './cookies.txt'

# Directory to save the downloaded MP3 files
output_directory = './lexscrape2'

# Ensure the output directory exists
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Function to extract age-restricted URLs from the nohup.out file
def extract_age_restricted_urls(nohup_file_path):
    age_restricted_urls = []
    with open(nohup_file_path, 'r') as file:
        for line in file:
            if "is age restricted, and can't be accessed without logging in" in line:
                parts = line.split()
                url = parts[2][:-1]  # Remove the trailing colon
                age_restricted_urls.append(url)
    return age_restricted_urls

# Function to download videos using yt-dlp with cookies
def download_age_restricted_videos(urls, cookies_file_path, output_directory):
    for url in urls:
        try:
            command = [
                'yt-dlp',
                '--cookies', cookies_file_path,
                '-f', 'bestaudio',
                '-x',
                '--audio-format', 'mp3',
                '-o', os.path.join(output_directory, '%(title)s.%(ext)s'),
                url
            ]
            subprocess.run(command, check=True)
            print(f"Successfully downloaded: {url}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading {url}: {e}")

# Extract age-restricted URLs from the nohup.out file
age_restricted_urls = extract_age_restricted_urls(nohup_file_path)

# Download age-restricted videos using yt-dlp with cookies
download_age_restricted_videos(age_restricted_urls, cookies_file_path, output_directory)
