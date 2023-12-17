import PySimpleGUI as sg
from pytube import YouTube
import threading, subprocess, os, ffmpeg, re
from pathlib import Path

# Add the FFmpeg binary directory to the PATH
ffmpeg_path = "./ffmpeg/bin"
os.environ["PATH"] += os.pathsep + os.path.abspath(ffmpeg_path)

# ====== Functions ====== #

def download_youtube_video(YouTubeURL, output_path, chosen_resolution):
    try:
        window["-STREAM_INFO_BUTTON-"].update(disabled=True)
        window["-BUTTON_DOWNLOAD-"].update(disabled=True)
        window["-PBAR-"].update(0)
        window["-OUTPUT_WINDOW-"].update("")

        def progress_callback(stream, chunk, remaining_bytes):
            total_size = stream.filesize
            bytes_downloaded = total_size - remaining_bytes
            percentage = (bytes_downloaded / total_size) * 100
            progress_text = f"Downloaded {bytes_downloaded}/{total_size}\n"

            # window["-OUTPUT_WINDOW-"].update(progress_text)
            window["-PBAR-"].update(percentage)

        if len(chosen_resolution) != 0 and values["-DOWNLOAD_FORMAT-"] == "Video Format":
            window["-BUTTON_DOWNLOAD-"].update(disabled=True)
            window["-STREAM_INFO_BUTTON-"].update(disabled=True)
            window["-OUTPUT_WINDOW-"].print("Starting download and encoding... please wait.\n")
            yt = YouTube(YouTubeURL, use_oauth=False, allow_oauth_cache=True, on_progress_callback=progress_callback)

            # Filter video streams based on the chosen resolution and audio for getting the videos audio for later merging with FFMPEG
            video_streams = yt.streams.filter(only_video=True, progressive=False, file_extension="mp4", res=chosen_resolution)
            only_audio_stream = yt.streams.filter(progressive=False, mime_type="audio/webm", abr="160kbps", audio_codec="opus")

            # Find the first available stream with the chosen video quality
            chosen_video_stream = next((stream for stream in video_streams if stream.resolution == chosen_resolution), None)
            # Get the audio stream of the video, with acodec=opus and quality at 160kbps
            chosen_audio_stream = next((stream for stream in only_audio_stream if stream.audio_codec == "opus" and stream.abr == "160kbps"), None)
            
            # Check if there is at least one stream with the chosen resolution
            if video_streams:
                
                # Forbidden characters pattern in filename (Windows)
                forbidden_chars_pattern = r'[\\/:"?<>|]'
                
                # Sanitized filename for ffmpeg encoder
                sanitized_filename = yt.title.replace(" ","_")
                sanitized_filename_with_extension = f"{sanitized_filename}.{chosen_video_stream.subtype}" 
                
                # If the filename contains forbidden characters, delete them for VIDEO
                if re.search(forbidden_chars_pattern, sanitized_filename_with_extension):
                    cleared_sanitized_filename_with_extension = re.sub(forbidden_chars_pattern, '', sanitized_filename_with_extension)
                else:
                    cleared_sanitized_filename_with_extension = sanitized_filename_with_extension
                    
                # Filename without the forbidden characters and without the filetype extension
                cleared_filename_without_extension = cleared_sanitized_filename_with_extension.removesuffix(f".{chosen_video_stream.subtype}")
                
                # Download the selected video stream
                chosen_video_stream.download(output_path=output_path, filename=cleared_sanitized_filename_with_extension, skip_existing=True)
                # Download the audio stream of the video
                chosen_audio_stream.download(output_path=output_path, filename="audio.webm", skip_existing=True)
                
                # FFmpeg extract audio and add it to the downloaded video
                input_video_file  = os.path.join(output_path, cleared_sanitized_filename_with_extension) # video file
                temp_audio_file = os.path.join(output_path, "audio.webm") # audio file for merging
                output_video_with_audio = os.path.join(output_path, f"{cleared_filename_without_extension}_.mp4") # merged audio and video file
                
                # FFmpeg command for merging audio and video
                ffmpeg.input(input_video_file).output(output_video_with_audio, vf='pad=ceil(iw/2)*2:ceil(ih/2)*2', acodec='opus', strict='experimental').run(overwrite_output=True)

                # Remove the temporary audio file
                os.remove(temp_audio_file)

                # Replace underscore (_) with whitespaces again for the encoded file
                replace_with_whitespaces = output_video_with_audio.replace("_", " ")
                os.rename(output_video_with_audio, replace_with_whitespaces)
                
                # Remove the video file
                os.remove(input_video_file)
                
                window["-OUTPUT_WINDOW-"].update(f"{yt.title} (Quality: {chosen_video_stream.resolution})\nhas been successfully downloaded.\nSaved in {output_path}")
            else:
                window["-OUTPUT_WINDOW-"].update(f"No video stream found with resolution: {chosen_resolution}\nPerhaps it's the wrong format?\nIf so, press Stream Info button again to reload the list.")

            window["-BUTTON_DOWNLOAD-"].update(disabled=False)
            window["-STREAM_INFO_BUTTON-"].update(disabled=False)
            window["-PBAR-"].update(0)
        else:
            window["-OUTPUT_WINDOW-"].update("ERROR: Select a Quality of Stream first.")
            window["-BUTTON_DOWNLOAD-"].update(disabled=False)
            window["-STREAM_INFO_BUTTON-"].update(disabled=False)
            window["-PBAR-"].update(0)
            
    except Exception as e:
        window["-OUTPUT_WINDOW-"].update("")
        window["-OUTPUT_WINDOW-"].print(f"ERROR: {e}")
        window["-OUTPUT_WINDOW-"].print(ffmpeg)
        window["-BUTTON_DOWNLOAD-"].update(disabled=False)
        window["-STREAM_INFO_BUTTON-"].update(disabled=False)
        window["-PBAR-"].update(0)

def download_youtube_audio(YouTubeURL, output_path, chosen_audio_quality):
    try:
        window["-STREAM_INFO_BUTTON-"].update(disabled=True)
        window["-BUTTON_DOWNLOAD-"].update(disabled=True)
        window["-PBAR-"].update(0)
        window["-OUTPUT_WINDOW-"].update("")

        def progress_callback(stream, chunk, remaining_bytes):
            total_size = stream.filesize
            bytes_downloaded = total_size - remaining_bytes
            percentage = (bytes_downloaded / total_size) * 100
            progress_text = f"Downloaded {bytes_downloaded}/{total_size}\n"
            window["-PBAR-"].update(percentage)

        if len(chosen_audio_quality) != 0 and values["-DOWNLOAD_FORMAT-"] == "Audio Format":
            window["-STREAM_INFO_BUTTON-"].update(disabled=True)
            window["-OUTPUT_WINDOW-"].print("Starting download and ffmpeg encoder... please wait.\n")
            yt = YouTube(YouTubeURL, use_oauth=False, allow_oauth_cache=True, on_progress_callback=progress_callback)

            # Filter audio streams based on the chosen quality
            audio_streams = yt.streams.filter(only_audio=True)

            # Find the first available stream with the chosen audio quality
            chosen_audio_stream = next((stream for stream in audio_streams if stream.abr == chosen_audio_quality), None)

            if chosen_audio_stream:
                
                # Forbidden characters in filename pattern
                forbidden_chars_pattern = r'[\\/:"?<>|]'
                
                # Sanitize the filename by replacing spaces with underscores
                sanitized_filename = yt.title.replace(" ","_")
                sanitized_filename_with_extension = sanitized_filename + "." + chosen_audio_stream.subtype
                
                # If the filename contains forbidden characters, delete them in an if clause
                if re.search(forbidden_chars_pattern, sanitized_filename_with_extension):
                    cleared_sanitized_filename_with_extension = re.sub(forbidden_chars_pattern, '', sanitized_filename_with_extension)
                else:
                    cleared_sanitized_filename_with_extension = sanitized_filename_with_extension
                cleared_filename_without_extension = cleared_sanitized_filename_with_extension.removesuffix(f".{chosen_audio_stream.subtype}")
                
                # Download the chosen audio stream
                chosen_audio_stream.download(output_path=output_path, filename=cleared_sanitized_filename_with_extension, skip_existing=True)
                
                # FFmpeg conversion to MP3
                input_file = os.path.join(output_path, cleared_sanitized_filename_with_extension)
                output_file = os.path.join(output_path, f"{cleared_filename_without_extension}.mp3")
                print(input_file)
                print(output_file)
                subprocess.run(['ffmpeg', '-i', input_file, '-vn', '-ar', '44100', '-ac', '2', '-b:a', '192k', output_file], capture_output=True)
                os.remove(input_file)
                
                # Replace underscore (_) with whitespaces again for the encoded file
                replace_with_whitespaces = output_file.replace("_"," ")
                os.rename(output_file, replace_with_whitespaces)
                
                window["-OUTPUT_WINDOW-"].update(f"{yt.title} (Quality: {chosen_audio_stream.abr})\nhas been successfully downloaded and converted to MP3.\nSaved in {output_path}")
            else:
                window["-OUTPUT_WINDOW-"].update(f"No audio stream found with quality: {chosen_audio_quality}\nPerhaps it's the wrong format?\nIf so, press Stream Info button again to reload the list.")

            window["-BUTTON_DOWNLOAD-"].update(disabled=False)
            window["-STREAM_INFO_BUTTON-"].update(disabled=False)
            window["-PBAR-"].update(0)
        else:
            window["-OUTPUT_WINDOW-"].update("ERROR: Select a Quality of Stream first.")
            window["-BUTTON_DOWNLOAD-"].update(disabled=False)
            window["-STREAM_INFO_BUTTON-"].update(disabled=False)
            window["-PBAR-"].update(0)

    except Exception as e:
        window["-OUTPUT_WINDOW-"].update("")
        window["-OUTPUT_WINDOW-"].print(f"ERROR: {e}")
        window["-BUTTON_DOWNLOAD-"].update(disabled=False)
        window["-STREAM_INFO_BUTTON-"].update(disabled=False)
        window["-PBAR-"].update(0)

def video_stream(YouTubeURL):
    try:
        window["-BUTTON_DOWNLOAD-"].update(disabled=True)
        window["-STREAM_INFO_BUTTON-"].update(disabled=True)
        yt = YouTube(YouTubeURL)
        window["-OUTPUT_WINDOW-"].update(f"Video Title: {yt.title}")
        window["-OUTPUT_WINDOW-"].print("\nLoading... please wait.\n")
        window["-OUTPUT_WINDOW-"].print("Available Video Streams:\n")
        # Filter streams and exclude those with video_codec=None
        video_streams = [stream for stream in yt.streams.filter(progressive=False, file_extension="mp4") if stream.video_codec is not None and stream.resolution and int(stream.resolution[:-1]) >= 480]
        # Collect resolutions in a list
        resolutions = [stream.resolution for stream in video_streams]
        for stream in video_streams:
            window["-OUTPUT_WINDOW-"].print(f"Resolution: {stream.resolution}, FPS: {stream.fps}, Codec: {stream.subtype}, Filesize: {stream.filesize / (1024 * 1024):.2f} MB")
            window["-QUALITY_FORMAT-"].update(values=resolutions)
        window["-BUTTON_DOWNLOAD-"].update(disabled=False)
        window["-STREAM_INFO_BUTTON-"].update(disabled=False)
    except Exception as e:
        window["-OUTPUT_WINDOW-"].update(f"ERROR: {e}")
        window["-BUTTON_DOWNLOAD-"].update(disabled=False)
        window["-STREAM_INFO_BUTTON-"].update(disabled=False)

def audio_stream(YouTubeURL):
    try:
        window["-BUTTON_DOWNLOAD-"].update(disabled=True)
        window["-STREAM_INFO_BUTTON-"].update(disabled=True)
        yt = YouTube(YouTubeURL)
        window["-OUTPUT_WINDOW-"].update(f"Video Title: {yt.title}")
        window["-OUTPUT_WINDOW-"].print("\nLoading... please wait.\n")
        window["-OUTPUT_WINDOW-"].print("Available Audio Streams:\n")
        audio_streams = yt.streams.filter(only_audio=True)
        abrs = [stream.abr for stream in audio_streams]  # Collect audio quality (abr) in a list
        for stream in audio_streams:
            window["-OUTPUT_WINDOW-"].print(f"Abr: {stream.abr}, Codec: {stream.subtype}, Filesize: {stream.filesize / (1024 * 1024):.2f} MB")
            window["-QUALITY_FORMAT-"].update(values=abrs)
        window["-BUTTON_DOWNLOAD-"].update(disabled=False)
        window["-STREAM_INFO_BUTTON-"].update(disabled=False)
    except Exception as e:
        window["-OUTPUT_WINDOW-"].update(f"ERROR: {e}")
        window["-BUTTON_DOWNLOAD-"].update(disabled=False)
        window["-STREAM_INFO_BUTTON-"].update(disabled=False)

# ====== GUI Theme ======#
my_new_theme = {'BACKGROUND': '#1c1e23',
                'TEXT': '#d2d2d3',
                'INPUT': '#3d3f46',
                'TEXT_INPUT': '#d2d2d3',
                'SCROLL': '#1c1e23',
                'BUTTON': ('white', '#c63a3d'),
                'PROGRESS': ('#778eca', '#c63a3d'),
                'BORDER': 1,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 0}

# Add your dictionary to the PySimpleGUI themes
sg.theme_add_new('MyRed', my_new_theme)

# Switch your theme to use the newly added one. You can add spaces to make it more readable
sg.theme("MyRed")

# ====== GUI LAYOUT ====== #
column_description = [[sg.Text("YouTube Downloader", font="Arial 20 bold underline", text_color="#c63a3d")],
                      [sg.Text("A YouTube Downloader built with Python and PySimpleGUI.")]]

column_file_save_location = [[sg.Text("Where to save", font="Arial 16 bold underline", text_color="#c63a3d")],
                      [sg.Text("Choose a location where you want to save downloads")],
                      [sg.Text("Save Location:"), sg.Input(default_text="C:/Users/Jovan/Pictures",size=(40,1), key="-SAVE_TO_FOLDER-"), sg.FolderBrowse(size=(10, 1))]]

column_download_layout = [[sg.Text("Downloading Part", font="Arial 16 bold underline", text_color="#c63a3d")],
                          [sg.Text("Stream type and quality settings:")],
                          [sg.Text("Type of stream to download:   "), sg.Combo(["Audio Format", "Video Format"],default_value="Audio Format", readonly=True, enable_events=True, key="-DOWNLOAD_FORMAT-")],
                          [sg.Text("Quality of stream to download:"), sg.Combo("", readonly=True, key="-QUALITY_FORMAT-", size=(13, 1))],
                          [sg.Text("Add a 'https://www.youtube.com/' link in the input box below:")],
                          [sg.Text("Enter URL Link:"), sg.Input(default_text="https://www.youtube.com/watch?v=mlu7ic_tmf4",key="-LINK_INPUT-", size=(31, 1)), sg.Button("Download", key="-BUTTON_DOWNLOAD-"), sg.Button("Stream Info", key="-STREAM_INFO_BUTTON-")]]

column_output_and_progressbar = [[sg.Multiline(size=(65, 10), key="-OUTPUT_WINDOW-")],
                                 [sg.Text("Progress:"), sg.ProgressBar(100, size=(45, 25), key="-PBAR-"), sg.Button("Exit", key="-EXIT-", size=(7, 1)), sg.Button("Clear", size=(7, 1), key="-CLEAR_OUTPUT-", tooltip="Clears Output Window and Progressbar if stuck.")]]

layout = [[sg.Column(column_description)],
          [sg.Column(column_file_save_location)],
          [sg.Column(column_download_layout)],
          [sg.Column(column_output_and_progressbar, justification="center")]]

# ====== GUI Events ======#
window = sg.Window("YouTube Downloader", layout, font="Arial 16", finalize=True)

# Event loop to process "events" and get the "values" of the inputs
while True:

    event, values = window.read()

    # ----Closing the programm with either option [X] or just by pressing "Exit"----#
    if (event == sg.WIN_CLOSED or event == "-EXIT-"):
        break

    if event == "-BUTTON_DOWNLOAD-" and values["-DOWNLOAD_FORMAT-"] == "Video Format":
    
        if len(values["-SAVE_TO_FOLDER-"]) == 0:
            window["-OUTPUT_WINDOW-"].update(
                "ERROR: Please enter a path where to save the video download.")
        elif len(values["-LINK_INPUT-"]) == 0:
            window["-OUTPUT_WINDOW-"].update(
                "ERROR: Please enter a valid YouTube link for video download.")
        else:
            download_thread = threading.Thread(target=download_youtube_video, args=(
                values["-LINK_INPUT-"], values["-SAVE_TO_FOLDER-"], values["-QUALITY_FORMAT-"]))
            download_thread.start()

    elif event == "-BUTTON_DOWNLOAD-" and values["-DOWNLOAD_FORMAT-"] == "Audio Format":
    
        if len(values["-SAVE_TO_FOLDER-"]) == 0:
            window["-OUTPUT_WINDOW-"].update(
                "ERROR: Please enter a path where to save the audio download.")
        elif len(values["-LINK_INPUT-"]) == 0:
            window["-OUTPUT_WINDOW-"].update(
                "ERROR: Please enter a valid YouTube link for audio download.")
        else:
            download_thread = threading.Thread(target=download_youtube_audio, args=(
                values["-LINK_INPUT-"], values["-SAVE_TO_FOLDER-"], values["-QUALITY_FORMAT-"]))
            download_thread.start()

    elif event == "-STREAM_INFO_BUTTON-" and values["-DOWNLOAD_FORMAT-"] == "Video Format":
        if len(values["-LINK_INPUT-"]) > 0:
            get_video_stream_thread = threading.Thread(target=video_stream, args=(values["-LINK_INPUT-"],))
            get_video_stream_thread.start()
        else:
            window["-OUTPUT_WINDOW-"].update("ERROR: Cannot get info of video stream because link input is empty.")

    elif event == "-STREAM_INFO_BUTTON-" and values["-DOWNLOAD_FORMAT-"] == "Audio Format":
      if len(values["-LINK_INPUT-"]) > 0:
          get_audio_stream_thread = threading.Thread(target=audio_stream, args=(values["-LINK_INPUT-"],))
          get_audio_stream_thread.start()
      else:
          window["-OUTPUT_WINDOW-"].update("ERROR: Cannot get info of audio stream because link input is empty.")

    elif event == "-CLEAR_OUTPUT-":
        window["-OUTPUT_WINDOW-"].update("")
        window["-PBAR-"].update(0)

window.close()