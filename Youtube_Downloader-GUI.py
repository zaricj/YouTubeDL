import PySimpleGUI as sg
from pytube import YouTube
from pytube.query import StreamQuery
import threading
import queue
from os import listdir
from os.path import isfile, join
import os

#====== Variables ======#

# Create a queue for communication between threads
update_queue = queue.Queue()

#====== Functions ======#

def download_youtube_video(YouTubeURL, output_path):
    try:
        def progress_callback(stream, chunk, remaining_bytes):
            total_size = stream.filesize
            bytes_downloaded = total_size - remaining_bytes
            percentage = (bytes_downloaded / total_size) * 100
            progress_text = f"Downloaded {bytes_downloaded}/{total_size}\n"
            
            window["-OUTPUT_WINDOW-"].update(progress_text)
            window["-PBAR-"].update(percentage)

        yt = YouTube(YouTubeURL, use_oauth=False, allow_oauth_cache=True, on_progress_callback=progress_callback)

        video = yt.streams.filter(file_extension="mp4")
        download_video = video.download(output_path=output_path)
        base,extension = os.path.splitext(download_video)
        new_video_filename = base + ".mp4"
        os.rename(download_video,new_video_filename)
        window["-OUTPUT_WINDOW-"].print(f"{yt.title}\nhas been successfully downloaded.\nSaved in {output_path}")
    
    except Exception as e:
        window["-OUTPUT_WINDOW-"].print(f"ERROR: {e}")
        
def download_youtube_audio(YouTubeURL, output_path):
    try:
        def progress_callback(stream, chunk, remaining_bytes):
            total_size = stream.filesize
            bytes_downloaded = total_size - remaining_bytes
            percentage = (bytes_downloaded / total_size) * 100
            progress_text = f"Downloaded {bytes_downloaded}/{total_size}\n"
            
            while bytes_downloaded < total_size:
                window["-OUTPUT_WINDOW-"].update(progress_text)
                window["-PBAR-"].update(0,max=100) # Sets the max_value of pg.Progressbar to the length of the predefined package list
                print("debug")
                window["-PBAR-"].update(current_count= 0 + percentage) # Updates the progress bar step by step with the length of the predefined package list
            
        yt = YouTube(YouTubeURL, use_oauth=False,allow_oauth_cache=True,on_progress_callback=progress_callback)
        
        music = yt.streams.filter(only_audio=True).first()
        download_music = music.download(output_path=output_path)
        base,extension = os.path.splitext(download_music)
        new_music_filename = base + ".mp3"
        os.rename(download_music,new_music_filename)
        window["-OUTPUT_WINDOW-"].print(f"{yt.title}\nhas been successfully downloaded.\nSaved in {output_path}")
        
    except Exception as e:
        window["-OUTPUT_WINDOW-"].print(f"ERROR: {e}")

def video_stream(YouTubeURL):
    yt = YouTube(YouTubeURL)
    window["-OUTPUT_WINDOW-"].print(f"Video Title: {yt.title}")
    window["-OUTPUT_WINDOW-"].print("Available Video Streams: Loading... please wait.")
    video_streams = yt.streams.filter(only_video=True, progressive=False, subtype="mp4").all()
    resolutions = [stream.resolution for stream in video_streams]  # Collect resolutions in a list
    for stream in video_streams:
        window["-OUTPUT_WINDOW-"].print(f"Resolution: {stream.resolution}, Codec: {stream.subtype}, Filesize: {stream.filesize / (1024 * 1024):.2f} MB")
    # Update the "-VIDEO_QUALITY-" combo element with the resolutions list
    window["-VIDEO_QUALITY-"].update(values=resolutions)

def audio_stream(YouTubeURL):
    yt = YouTube(YouTubeURL)
    window["-OUTPUT_WINDOW-"].print(f"Video Title:{yt.title}")
    window["-OUTPUT_WINDOW-"].print("Available Audio Streams: Loading... please wait.")
    audio_streams = yt.streams.filter(only_audio=True, progressive=False).all()
    abrs = [stream.abr for stream in audio_streams]  # Collect audio quality (abr) in a list
    for stream in audio_streams:
        window["-OUTPUT_WINDOW-"].print(f"Abr: {stream.abr}, Filesize: {stream.filesize / (1024 * 1024):.2f} MB")
    # Update the "-AUDIO_QUALITY-" combo element with the abrs list
    window["-AUDIO_QUALITY-"].update(values=abrs)

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

audio_quality_list = [""]
video_quality_list = [""]

#====== GUI LAYOUT ======#
column_description = [[sg.Text("YouTube Downloader", font="Arial 20 bold underline",text_color="#c63a3d")],
                      [sg.Text("A YouTube Downloader built with Python and PySimpleGUI.")],
                      [sg.Text("Global Settings", font="Arial 16 bold underline", text_color="#c63a3d")],
                      [sg.Text("Choose a location where you want to save the Files")],
                      [sg.Text("Save File to:"),sg.Input(key="-SAVE_TO_FOLDER-"),sg.FolderBrowse(size=(10,1))]]

column_video_downloader = [[sg.Text("Video Download", font="Arial 20 bold underline",text_color="#c63a3d")],
                           [sg.Text("This input is used for Video downloading:")],
                           [sg.Text("Enter URL Link"),sg.Input(key="-VIDEO_INPUT-"),sg.Button("Download", key="-BUTTON_DOWNLOAD_VIDEO-")],
                           [sg.Text("Choose Quality:"),sg.Combo(video_quality_list,size=(10,1),key="-VIDEO_QUALITY-"),sg.Button("Get Stream",key="-VIDEO_STREAM_BUTTON-")]]

column_audio_downloader = [[sg.Text("Audio Download", font="Arial 20 bold underline",text_color="#c63a3d")],
                           [sg.Text("This input is used for Audio downloading:")],
                           [sg.Text("Enter URL Link"),sg.Input(key="-AUDIO_INPUT-"),sg.Button("Download", key="-BUTTON_DOWNLOAD_AUDIO-")],
                           [sg.Text("Choose Quality:"),sg.Combo(audio_quality_list,size=(10,1),key="-AUDIO_QUALITY-"),sg.Button("Get Stream",key="-AUDIO_STREAM_BUTTON-")]]

column_output_and_progressbar = [[sg.Multiline(size=(65,10),key="-OUTPUT_WINDOW-")],
                        [sg.Text("Progress:"),sg.ProgressBar(100,size=(45,25),key="-PBAR-"),sg.Button("Exit", key="-EXIT-", size=(7,1)),sg.Button("Clear",size=(7,1), key="-CLEAR_OUTPUT-")]]

layout = [[sg.Column(column_description)],
          [sg.HSeparator()],
          [sg.Column(column_video_downloader)],
          [sg.Column(column_audio_downloader)],
          [sg.Column(column_output_and_progressbar, justification="center")]]

#====== GUI Events ======#
window = sg.Window("YouTube Downloader",layout,font="Arial 16",finalize=True)

# Event loop to process "events" and get the "values" of the inputs
while True:
    
    event,values = window.read()
    
        #----Closing the programm with either option the [X] or just by pressing "Exit"----#
    if (event == sg.WIN_CLOSED or event == "-EXIT-"):
        break
    
    if event == "-BUTTON_DOWNLOAD_VIDEO-":
        if len(values["-SAVE_TO_FOLDER-"]) == 0:
            window["-OUTPUT_WINDOW-"].update("Please enter a path where to save to the downloaded file.")
        elif len(values["-VIDEO_INPUT-"]) == 0:
            window["-OUTPUT_WINDOW-"].update("Please enter a YouTube link for Video Download.")
        else:
            download_thread = threading.Thread(target=download_youtube_video, args=(values["-VIDEO_INPUT-"], values["-SAVE_TO_FOLDER-"]))
            download_thread.start()
            #window.perform_long_operation(lambda:download_youtube_video(YouTubeURL = values["-VIDEO_INPUT-"],output_path = values["-SAVE_TO_FOLDER-"]),"-OUTPUT_WINDOW-")
        
    elif event == "-BUTTON_DOWNLOAD_AUDIO-":
        if len(values["-SAVE_TO_FOLDER-"]) == 0:
            window["-OUTPUT_WINDOW-"].update("Please enter a path where to save to the downloaded file.")
        elif len(values["-AUDIO_INPUT-"]) == 0:
            window["-OUTPUT_WINDOW-"].update("Please enter a YouTube link for Audio Download.")
        else:
           download_thread = threading.Thread(target=download_youtube_audio, args=(values["-AUDIO_INPUT-"], values["-SAVE_TO_FOLDER-"]))
           download_thread.start()
            #window.perform_long_operation(lambda:download_youtube_audio(YouTubeURL = values["-AUDIO_INPUT-"],output_path = values["-SAVE_TO_FOLDER-"]),"-OUTPUT_WINDOW-")
    
    elif event == "-VIDEO_STREAM_BUTTON-":
        if len(values["-VIDEO_INPUT-"]):
            get_video_stream_thread = threading.Thread(target=video_stream, args=(values["-VIDEO_INPUT-"],))
            get_video_stream_thread.start()

    elif event == "-AUDIO_STREAM_BUTTON-":
        if len(values["-AUDIO_INPUT-"]):
            get_audio_stream_thread = threading.Thread(target=audio_stream, args=(values["-AUDIO_INPUT-"],))
            get_audio_stream_thread.start()
            
    elif event == "-CLEAR_OUTPUT-":
            window["-OUTPUT_WINDOW-"].update("")
            window["-PBAR-"].update(0)
    
window.close()