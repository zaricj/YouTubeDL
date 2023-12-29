# YouTube Downloader
### Description
A YouTube Downloader GUI built in Python with the amazing PySimpleGUI, it uses the pytube module for downloading audio and videos from youtube and FFmpeg to convert the audio files which are usually .mp4 or .webm to .mp3 and merging audio/video together since I am using the Adaprive Streams from YouTube so it downloads videos at the specified Quality without sound.

### Requirements
- Python
- FFmpeg
- pysimplegui
- pytube
- webbrowser
- pathlib

### FFmpeg is requiered for encoding and merging video/audio files!
FFmpeg is a hard requirement since it's being used in the code.

The code WILL not run if you don't have FFmpeg, also you have to add FFmpeg to the Enviromental Path too!

#### Links to get FFmpeg:
- Link to FFmpeg's Homepage: [FFmpeg](https://www.ffmpeg.org/)
- Quick link to FFmpeg for Windows only: [FFmpeg For Windows](https://www.gyan.dev/ffmpeg/builds/)

### Usage
#### How to use the Program step by step:
- Choose a Path where to save files with the Browser button
- Choose a Type of Stream to download (Audio Format or Video Format)
- Quality of Stream to download, this is a listbox from PySimpleGUI. It is empty at first, in order to initialise it, add a 'https://www.youtube.com/watch' link to the 'URL Link' inputbox and press the STREAM INFO button. The listbox will be filled appropriately based on the selected 'Type of Stream to download'.
- Now select a Quality of Stream from the list, ex. 1080 for a 1080P video, if you have chosen the Video Format option.
- Press Download and see the magic happen!

### Functionality I want to add in the future:

- A listbox to add multiple Links to download and a '+ Button' to append URLs to the listbox.

# Screenshot of the Program
![image](https://github.com/zaricj/YouTubeDL/assets/93329694/8bd2aa6f-a112-4a0c-b5d8-7691d8f9024b)

# Screenshot of Program with Listbox function
![python_rfzo2ZKTlC](https://github.com/zaricj/YouTubeDL/assets/93329694/fe3d4579-cd63-495a-bc42-3d0858c4dbf6)
