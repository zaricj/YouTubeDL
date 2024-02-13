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

get_audio_streams = yt.streams.filter(type="audio",adaptive=True, mime_type="audio/mp4").order_by("abr")
get_video_streams = yt.streams.filter(type="video", adaptive=True, mime_type="video/mp4").order_by("resolution")

get_audio_quality_only = [stream.abr for stream in get_audio_streams]
get_resolutions_only = [stream.resolution for stream in get_video_streams]

print(f"Avaiable Resolutions: {get_resolutions_only}")
print(f"Avaiable Audio Quality: {get_audio_quality_only}")
print("")

for index,stream in enumerate(get_audio_streams,0):
    print(f"\n{index}. || {stream}")
print("__________________________________________")
for index,stream in enumerate(get_video_streams,0):
    print(f"\n{index}. || {stream}")