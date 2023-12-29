from pytube import YouTube
from pathlib import Path
import threading 
import subprocess 
import os 
import ffmpeg
import re

from pytube import YouTube

yt_url = "https://www.youtube.com/watch?v=yoYZf-lBF_U" # 2Pac - AAR

yt = YouTube(yt_url)

print(f"Title of Video: {yt.title}")

get_video_streams = yt.streams.filter(only_audio=True,audio_codec="opus")
get_resolutions_only = [stream.abr for stream in get_video_streams]

print(f"Avaiable Resolutions: {get_resolutions_only}")
print(f"Video Streams: \n {get_video_streams}")

for index,stream in enumerate(get_video_streams,0):
    print(f"\n{index}. || {stream}")