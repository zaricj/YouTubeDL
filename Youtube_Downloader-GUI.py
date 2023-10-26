import PySimpleGUI as sg
from pytube import YouTube
import threading
import queue

# Create a queue for communication between threads
update_queue = queue.Queue()

#====== Functions ======#

def download_youtube_video(YouTubeURL, output_path):
    try:
        window["-PBAR-"].update(0)
        window["-OUTPUT_WINDOW-"].update("")
        def progress_callback(stream, chunk, remaining_bytes):
            total_size = stream.filesize
            bytes_downloaded = total_size - remaining_bytes
            percentage = (bytes_downloaded / total_size) * 100
            progress_text = f"Downloaded {bytes_downloaded}/{total_size}\n"
            
            # window["-OUTPUT_WINDOW-"].update(progress_text)
            window["-PBAR-"].update(percentage)
            
        window["-BUTTON_DOWNLOAD_VIDEO-"].update(disabled=True)
        window["-VIDEO_STREAM_BUTTON-"].update(disabled=True)
        window["-OUTPUT_WINDOW-"].print("Starting download... please wait.\n")
        yt = YouTube(YouTubeURL, use_oauth=False, allow_oauth_cache=True, on_progress_callback=progress_callback)

        video = yt.streams.get_highest_resolution()
        video.download(output_path=output_path, skip_existing=True)
        window["-OUTPUT_WINDOW-"].print(f"{yt.title} (Quality: {video.resolution})\nhas been successfully downloaded.\nSaved in {output_path}")
        window["-BUTTON_DOWNLOAD_VIDEO-"].update(disabled=False)
        window["-VIDEO_STREAM_BUTTON-"].update(disabled=False)
        window["-PBAR-"].update(0)
    except Exception as e:
        window["-OUTPUT_WINDOW-"].update("")
        window["-OUTPUT_WINDOW-"].print(f"ERROR: {e}")
        window["-BUTTON_DOWNLOAD_VIDEO-"].update(disabled=False)
        window["-VIDEO_STREAM_BUTTON-"].update(disabled=False)
        
def download_youtube_audio(YouTubeURL, output_path):
    try:
        window["-PBAR-"].update(0)
        window["-OUTPUT_WINDOW-"].update("")
        def progress_callback(stream, chunk, remaining_bytes):
            total_size = stream.filesize
            bytes_downloaded = total_size - remaining_bytes
            percentage = (bytes_downloaded / total_size) * 100
            progress_text = f"Downloaded {bytes_downloaded}/{total_size}\n"
            
            #window["-OUTPUT_WINDOW-"].update(progress_text)
            window["-PBAR-"].update(percentage)
        
        values["-BUTTON_DOWNLOAD_AUDIO-"].update(disabled=True)
        window["-AUDIO_STREAM_BUTTON-"].update(disabled=True)
        window["-OUTPUT_WINDOW-"].print("Starting download... please wait.\n") 
        yt = YouTube(YouTubeURL, use_oauth=False,allow_oauth_cache=True,on_progress_callback=progress_callback)
        
        music = yt.streams.get_audio_only()
        music.download(output_path=output_path,skip_existing=True)
        window["-OUTPUT_WINDOW-"].print(f"{yt.title} (Quality: {music.abr})\nhas been successfully downloaded.\nSaved in {output_path}")
        window["-BUTTON_DOWNLOAD_AUDIO-"].update(disabled=False)
        window["-AUDIO_STREAM_BUTTON-"].update(disabled=False)
        window["-PBAR-"].update(0)
    except Exception as e:
        window["-OUTPUT_WINDOW-"].update("")
        window["-OUTPUT_WINDOW-"].print(f"ERROR: {e}")
        window["-BUTTON_DOWNLOAD_AUDIO-"].update(disabled=False)
        window["-AUDIO_STREAM_BUTTON-"].update(disabled=False)

def video_stream(YouTubeURL):
    yt = YouTube(YouTubeURL)
    window["-OUTPUT_WINDOW-"].print(f"Video Title: {yt.title}")
    window["-OUTPUT_WINDOW-"].print("Available Video Streams: Loading... please wait.")
    video_streams = yt.streams.filter(only_video=True, progressive=False, subtype="mp4")
    resolutions = [stream.resolution for stream in video_streams]  # Collect resolutions in a list
    for stream in video_streams:
        window["-OUTPUT_WINDOW-"].print(f"Resolution: {stream.resolution}, Codec: {stream.subtype}, Filesize: {stream.filesize / (1024 * 1024):.2f} MB")

def audio_stream(YouTubeURL):
    yt = YouTube(YouTubeURL)
    window["-OUTPUT_WINDOW-"].print(f"Video Title: {yt.title}")
    window["-OUTPUT_WINDOW-"].print("Available Audio Streams: Loading... please wait.")
    audio_streams = yt.streams.filter(only_audio=True, progressive=False)
    abrs = [stream.abr for stream in audio_streams]  # Collect audio quality (abr) in a list
    for stream in audio_streams:
        window["-OUTPUT_WINDOW-"].print(f"Abr: {stream.abr}, Filesize: {stream.filesize / (1024 * 1024):.2f} MB")

#====== GUI Theme ======#
my_new_theme = {'BACKGROUND': '#1c1e23',
                'TEXT': '#d2d2d3',
                'INPUT': '#41444d',
                'TEXT_INPUT': '#d2d2d3',
                'SCROLL': '#c7e78b',
                'BUTTON': ('white', '#c63a3d'),
                'PROGRESS': ('#59cf6e', '#41444d'),
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
                           [sg.Text("Enter URL Link"),sg.Input(key="-VIDEO_INPUT-",size=(33,1)),sg.Button("Download", key="-BUTTON_DOWNLOAD_VIDEO-"),sg.Button("Stream Info",key="-VIDEO_STREAM_BUTTON-")]]

column_audio_downloader = [[sg.Text("Audio Download", font="Arial 20 bold underline",text_color="#c63a3d")],
                           [sg.Text("This input is used for Audio downloading:")],
                           [sg.Text("Enter URL Link"),sg.Input(key="-AUDIO_INPUT-",size=(33,1)),sg.Button("Download", key="-BUTTON_DOWNLOAD_AUDIO-"),sg.Button("Stream Info",key="-AUDIO_STREAM_BUTTON-")]]

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
        
    elif event == "-BUTTON_DOWNLOAD_AUDIO-":
        if len(values["-SAVE_TO_FOLDER-"]) == 0:
            window["-OUTPUT_WINDOW-"].update("Please enter a path where to save to the downloaded file.")
        elif len(values["-AUDIO_INPUT-"]) == 0:
            window["-OUTPUT_WINDOW-"].update("Please enter a YouTube link for Audio Download.")
        else:
           download_thread = threading.Thread(target=download_youtube_audio, args=(values["-AUDIO_INPUT-"], values["-SAVE_TO_FOLDER-"]))
           download_thread.start()
    
    elif event == "-VIDEO_STREAM_BUTTON-":
        if len(values["-VIDEO_INPUT-"]) > 0:
            get_video_stream_thread = threading.Thread(target=video_stream, args=(values["-VIDEO_INPUT-"],))
            get_video_stream_thread.start()
        else:
            window["-OUTPUT_WINDOW-"].print("ERROR: Cannot get info of Video Stream because input is empty.")

    elif event == "-AUDIO_STREAM_BUTTON-":
        if len(values["-AUDIO_INPUT-"]) > 0:
            get_audio_stream_thread = threading.Thread(target=audio_stream, args=(values["-AUDIO_INPUT-"],))
            get_audio_stream_thread.start()
        else:
            window["-OUTPUT_WINDOW-"].print("ERROR: Cannot get info of Audio Stream because input is empty.")
                     
    elif event == "-CLEAR_OUTPUT-":
            window["-OUTPUT_WINDOW-"].update("")
            window["-PBAR-"].update(0)
    
window.close()
