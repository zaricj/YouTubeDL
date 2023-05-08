import PySimpleGUI as sg
from pytube import YouTube
import time
import logging
from os import listdir
from os.path import isfile, join
import os

#====== Variables ======#

#====== Functions ======#
def download_youtube_video(YouTubeURL, Save_To_Path):
    count = 0
    for progress in range(1,100):
        
        window["-PBAR-"].update(0)
        window["-PBAR-"].update(current_count = 0 + count)
        
        yt = YouTube(YouTubeURL, use_oauth=True, allow_oauth_cache=True)
        video = yt.streams.filter(file_extension="mp4")
        download_video = video.download(output_path=Save_To_Path)
        base,extension = os.path.splitext(download_video)
        new_video_filename = base + "mp4"
        os.rename(download_video,new_video_filename)
        window["-OUTPUT_WINDOW-"].print(f"{yt.title} has been successfully  downloaded.")
        
    window["-PBAR-"].update(0)
        
def download_youtube_audio(YouTubeURL, Save_To_Path):
    yt = YouTube(YouTubeURL, use_oauth=True, allow_oauth_cache=True)
    music = yt.streams.filter(only_audio=True).first()
    download_music = music.download(output_path=Save_To_Path)
    base,extension = os.path.splitext(download_music)
    new_music_filename = base + "mp3"
    os.rename(download_music,new_music_filename)
    window["-OUTPUT_WINDOW-"].print(f"{yt.title} has been successfully downloaded.")
    
#====== GUI Theme ======#
my_new_theme = {'BACKGROUND': '#1c1e23',
                'TEXT': '#d2d2d3',
                'INPUT': '#3d3f46',
                'TEXT_INPUT': '#d2d2d3',
                'SCROLL': '#c7e78b',
                'BUTTON': ('white', '#c63a3d'),
                'PROGRESS': ('#778eca', '#c63a3d'),
                'BORDER': 1,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 0}

# Add your dictionary to the PySimpleGUI themes
sg.theme_add_new('MyRed', my_new_theme)

# Switch your theme to use the newly added one. You can add spaces to make it more readable
sg.theme("MyRed")

#====== GUI LAYOUT ======#
column_description = [[sg.Text("YouTube Downloader", font="Arial 20 bold underline",text_color="#c63a3d")],
                      [sg.Text("A YouTube Downloader built with Python and PySimpleGUI.")],
                      [sg.Text("Global Settings", font="Arial 16 bold underline", text_color="#c63a3d")],
                      [sg.Text("Choose a location where you want to save the Files")],
                      [sg.Text("Save File to:"),sg.Input(key="-SAVE_TO_FOLDER-"),sg.FolderBrowse(size=(10,1))]]

column_video_downloader = [[sg.Text("Video Download", font="Arial 20 bold underline",text_color="#c63a3d")],
                           [sg.Text("This input is used for Video downloading:")],
                           [sg.Text("Enter URL Link"),sg.Input(key="-VIDEO_INPUT-"),sg.Button("Download", key="-BUTTON_DOWNLOAD_VIDEO-")]]

column_audio_downloader = [[sg.Text("Audio Download", font="Arial 20 bold underline",text_color="#c63a3d")],
                           [sg.Text("This input is used for Audio downloading:")],
                           [sg.Text("Enter URL Link"),sg.Input(key="-AUDIO_INPUT-"),sg.Button("Download", key="-BUTTON_DOWNLOAD_AUDIO-")]]

column_output_and_progressbar = [[sg.Multiline(size=(65,10),key="-OUTPUT_WINDOW-")],
                        [sg.Text("Progress:"),sg.ProgressBar(max_value=1,size=(45,25),key="-PBAR-"),sg.Button("Exit", key="-EXIT-", size=(7,1)),sg.Button("Clear",size=(7,1), key="-CLEAR_OUTPUT-")]]

layout = [[sg.Column(column_description)],
          [sg.HSeparator()],
          [sg.Column(column_video_downloader)],
          [sg.Column(column_audio_downloader)],
          [sg.Column(column_output_and_progressbar, justification="center")]]

#====== GUI Events ======#
window = sg.Window("YouTube Downloader",layout,font="Arial 16",finalize=True)

# Event loop to process "events" and get the "values" of the inputs
while True:
    
    event,values = window.read(timeout=1)
    
        #----Closing the programm with either option the [X] or just by pressing "Exit"----#
    if (event == sg.WIN_CLOSED or event == "-EXIT-"):
        break
    
    if event == "-BUTTON_DOWNLOAD_VIDEO-":
        window.perform_long_operation(lambda:download_youtube_video(YouTubeURL = values["-VIDEO_INPUT-"],Save_To_Path = values["-SAVE_TO_FOLDER-"]),"-OUTPUT_WINDOW-")
        
    elif event == "-BUTTON_DOWNLOAD_AUDIO-":
        window.perform_long_operation(lambda:download_youtube_audio(YouTubeURL = values["-AUDIO_INPUT-"],Save_To_Path = values["-SAVE_TO_FOLDER-"]),"-OUTPUT_WINDOW-")
        
    elif event == "-CLEAR_OUTPUT-":
            window["-OUTPUT_WINDOW-"].update("")
            window["-PBAR-"].update(current_count= 0 + 1)
            time.sleep(0.5)
            window["-PBAR-"].update(0)
        
window.close()
    
