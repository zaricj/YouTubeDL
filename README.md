# YouTube Downloader
### Description
This Python-based downloader utilizes the powerful PySimpleGUI library to provide a simple graphical interface. Download audio and videos from YouTube with ease! The pytube module handles efficient retrieval, while FFmpeg seamlessly converts downloaded audio files (typically .mp4 or .webm) to the popular .mp3 format. Additionally, the app merges audio and video back together, catering specifically to Adaptive Streams from YouTube. This allows you to download videos at your desired quality without sacrificing audio.

### Key Features:
- Intuitive graphical interface powered by PySimpleGUI
- Efficient downloads using pytube
- Effortless audio conversion (.mp4/.webm to .mp3) with FFmpeg
- Seamless merging of audio and video streams
- Optimized for downloading Adaptive Streams with separate audio/video

### Requirements
- Python
- FFmpeg
- pysimplegui
- pytube
- webbrowser
- pathlib

### Important Information
This downloader relies on FFmpeg for some key tasks like encoding audio and merging media files.

- FFmpeg is mandatory: Without it, the program won't function as intended.
- Installation required: Download and install FFmpeg from its official website (https://ffmpeg.org/download.html).
- Add to Path for convenience: Configure your system's "Environment Path" to include the FFmpeg installation directory. This allows the program to easily find and use FFmpeg.

### Usage
#### How to use the Program step by step:
1. Set Your Download Location
  - Click the "Browse" button and choose where you want your downloaded files to be saved. This ensures your videos and audio tracks land right where you need them.
2. Choose Your Media
  - Decide if you want to download the video with audio (Video Format) or just the audio track (Audio Format). This option allows you to customize your downloads depending on your needs.
3. Find Your Desired Quality
  - Enter a valid YouTube video URL in the "URL Link" field and click the "Get Stream" button. This retrieves available qualities for the video or audio, based on your chosen format.
4. Pick Your Quality
  - Once the list is populated, select the quality you prefer. For example, choose 1080p for a high-quality video download if your Stream Format is "Video Format", for audio choose a audio quality with it's corresponding bitrate if your Stream Format is "Audio Format".
5. Hit Download and Enjoy
  - Click the "Download" button and watch the magic happen! Your chosen video or audio file will be downloaded to your specified location.

### Functionality I want to add in the future:
- A listbox to add multiple Links to download and a '+ Button' to append URLs to the listbox.

# Screenshot of Program
![python_roXopHoCK5](https://github.com/zaricj/YouTubeDL/assets/93329694/491c2cba-cab8-42ac-9531-e5638e6d4de7)
