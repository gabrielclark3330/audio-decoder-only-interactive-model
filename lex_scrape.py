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
