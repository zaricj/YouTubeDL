import PySimpleGUI as sg
from pytube import YouTube
from pathlib import Path
import threading
import subprocess 
import os
import re 
import webbrowser
import re

def main():
    
# Add the FFmpeg binary directory to the PATH 
    # current_working_path = os.path.dirname(os.path.abspath(__file__)) # Current working Directory
    # print(current_working_path)
    ffmpeg_path = "./_internal/ffmpeg/bin"
    if ffmpeg_path:
        os.environ["PATH"] += os.pathsep + os.path.abspath(ffmpeg_path)
    else:
        print("No FFmpeg folder found")
        pass

    # ====== Functions ====== #
    def download_youtube_video(youtube_url, output_path, chosen_resolution):
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

                yt = YouTube(youtube_url, use_oauth=False, allow_oauth_cache=True, on_progress_callback=progress_callback)

                # Filter video streams based on the chosen resolution and audio for getting the videos audio for later merging with FFmpeg
                video_streams = yt.streams.filter(type="video", adaptive=True, mime_type="video/mp4")
                audio_streams = yt.streams.get_audio_only() # Get the highest quality audio stream of the video (128kbps)

                # Find the first available stream with the chosen video quality
                chosen_video_stream = next((stream for stream in video_streams if stream.resolution == chosen_resolution), None)

                # Check if there is at least one stream with the chosen resolution
                if video_streams:

                    # Forbidden characters pattern in filename (Windows)
                    forbidden_chars_pattern = r'[\\/:"?<>|]'

                    # Sanitized filename for ffmpeg encoder
                    sanitized_filename = yt.title.replace(" ","_")
                    sanitized_filename_with_extension = f"{sanitized_filename}.{chosen_video_stream.subtype}" 

                    # If the filename contains forbidden characters, delete them for VIDEO
                    if re.search(forbidden_chars_pattern, sanitized_filename_with_extension):
                        cleared_video_filename = re.sub(forbidden_chars_pattern, '', sanitized_filename_with_extension)
                    else:
                        cleared_video_filename = sanitized_filename_with_extension

                    # Download the selected video and audio stream
                    chosen_video_stream.download(output_path=output_path, filename=cleared_video_filename, skip_existing=True)
                    audio_streams.download(output_path=output_path, filename="audio.mp4", skip_existing=True)

                    # FFmpeg paths for the files
                    the_video_file = os.path.join(output_path, cleared_video_filename) # The Downloaded video file
                    the_audio_file =  os.path.join(output_path,"audio.mp4") # The Downloaded audio file
                    encoded_finished_filename = os.path.join(output_path,"encoded_video_with_audio.mp4") # Encoded File (merge audo/video)

                    # FFmpeg extract audio and add it to the downlaoded video 
                    subprocess.run(f"ffmpeg -i {the_video_file} -i {the_audio_file} -c copy {encoded_finished_filename}")

                    os.remove(the_audio_file) # Remove the downloaded audio file "audio.mp4"
                    os.remove(the_video_file) # Remove the downloaded audio file "yt.title.mp4"

                    # Rename the concatenated file to the original video file name
                    os.rename(encoded_finished_filename, the_video_file)

                    # Replace underscore (_) with whitespaces again for the encoded file
                    replace_with_whitespaces = the_video_file.replace("_", " ")
                    os.rename(the_video_file, replace_with_whitespaces)

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
            window["-BUTTON_DOWNLOAD-"].update(disabled=False)
            window["-STREAM_INFO_BUTTON-"].update(disabled=False)
            window["-PBAR-"].update(0)

    def download_youtube_audio(youtube_url, output_path, chosen_audio_quality):
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
                yt = YouTube(youtube_url, use_oauth=False, allow_oauth_cache=True, on_progress_callback=progress_callback)

                # Filter audio streams based on the chosen quality
                audio_streams = yt.streams.filter(type="audio",adaptive=True, mime_type="audio/mp4")

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
                        cleared_video_filename = re.sub(forbidden_chars_pattern, " ", sanitized_filename_with_extension)
                    else:
                        cleared_video_filename = sanitized_filename_with_extension
                    cleared_filename_without_extension = cleared_video_filename.removesuffix(f".{chosen_audio_stream.subtype}")

                    # Download the chosen audio stream
                    chosen_audio_stream.download(output_path=output_path, filename=cleared_video_filename, skip_existing=True)

                    # FFmpeg conversion to MP3
                    input_file = os.path.join(output_path, cleared_video_filename)
                    output_file = os.path.join(output_path, f"{cleared_filename_without_extension}.mp3")
                    subprocess.run(["ffmpeg", "-i", input_file, "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k", output_file], capture_output=True)
                    os.remove(input_file)

                    # Replace underscore (_) with whitespaces again for the encoded file
                    replace_with_whitespaces = output_file.replace("_"," ")
                    os.rename(output_file, replace_with_whitespaces)

                    window["-OUTPUT_WINDOW-"].update(f"{yt.title} (Quality: {chosen_audio_stream.abr})\nDownload completed and converted to MP3.\nDownloaded file saved in {output_path}")
                else:
                    window["-OUTPUT_WINDOW-"].update(f"No audio stream found with quality: {chosen_audio_quality}\nPerhaps it's the wrong format?\nIf so, press Get Stream button again to reload the list.")

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

    def video_stream(youtube_url):
        try:
            window["-BUTTON_DOWNLOAD-"].update(disabled=True)
            window["-STREAM_INFO_BUTTON-"].update(disabled=True)
            
            yt = YouTube(youtube_url)
            window["-OUTPUT_WINDOW-"].update(f"Video Title: {yt.title}")
            window["-OUTPUT_WINDOW-"].print("\nLoading... please wait.\n")
            window["-OUTPUT_WINDOW-"].print("Available Video Streams:\n")
            # Filter streams and exclude those with video_codec=None
            video_streams = [stream for stream in yt.streams.filter(type="video", adaptive=True, mime_type="video/mp4")]
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

    def audio_stream(youtube_url):
        try:
            window["-BUTTON_DOWNLOAD-"].update(disabled=True)
            window["-STREAM_INFO_BUTTON-"].update(disabled=True)
            yt = YouTube(youtube_url)
            window["-OUTPUT_WINDOW-"].update(f"Video Title: {yt.title}")
            window["-OUTPUT_WINDOW-"].print("\nLoading... please wait.\n")
            window["-OUTPUT_WINDOW-"].print("Available Audio Streams:\n")
            audio_streams = yt.streams.filter(type="audio",adaptive=True, mime_type="audio/mp4")
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
                    'PROGRESS': ('#03fc5a', '#c63a3d'),
                    'BORDER': 1,
                    'SLIDER_DEPTH': 0,
                    'PROGRESS_DEPTH': 0}

    # Add your dictionary to the PySimpleGUI themes
    sg.theme_add_new('MyRed', my_new_theme)

    # Switch your theme to use the newly added one. You can add spaces to make it more readable
    sg.theme("MyRed")

    MENU_RIGHT_CLICK = ["",["Clear Output", "Version", "Exit"]]
    MENU_RIGHT_CLICK_COPY_PASTE = ["&Right", ["&Copy", "&Paste"]]
    # ====== GUI LAYOUT ====== #
    column_description = [[sg.Text("YouTube Downloader", font="Arial 20 bold underline", text_color="#c63a3d")],
                          [sg.Text("A YouTube Downloader built with Python and PySimpleGUI.")],
                          [sg.Text("FFmpeg is required! You can get in here:"),sg.Text("FFmpeg for Windows",font="Arial 14 underline",text_color="#c63a3d",enable_events=True,tooltip="Direct link download to FFmpeg for Windows only.", key="-URL_REDIRECT-"),sg.Button("Check",size=(5,1),key="-CHECK_IF_FFMPEG_INSTALLED-")]]

    column_file_save_location = [[sg.Text("Where to save", font="Arial 16 bold underline", text_color="#c63a3d")],
                          [sg.Text("Choose a location where you want to save downloads")],
                          [sg.Text("Save Location:"), sg.Input(size=(40,1), key="-SAVE_TO_FOLDER-", right_click_menu=MENU_RIGHT_CLICK_COPY_PASTE), sg.FolderBrowse(size=(10, 1))]]

    column_download_layout = [[sg.Text("Downloading Part", font="Arial 16 bold underline", text_color="#c63a3d")],
                              [sg.Text("Stream type and quality settings:")],
                              [sg.Text("Type of stream to download:   "), sg.Combo(["Audio Format", "Video Format"],default_value="Audio Format", readonly=True, key="-DOWNLOAD_FORMAT-")],
                              [sg.Text("Quality of stream to download:"), sg.Combo("", readonly=True, key="-QUALITY_FORMAT-", size=(13, 1))],
                              [sg.Text("Add a 'https://www.youtube.com/' link in the input box below:")],
                              [sg.Text("Enter URL Link:"), sg.Input(key="-LINK_INPUT-", size=(31, 1), right_click_menu=MENU_RIGHT_CLICK_COPY_PASTE), sg.Button("Download", key="-BUTTON_DOWNLOAD-"), sg.Button("Get Stream", key="-STREAM_INFO_BUTTON-")]]

    column_output_and_progressbar = [[sg.Multiline(size=(65, 10), key="-OUTPUT_WINDOW-")],
                                     [sg.Text("Progress:"), sg.ProgressBar(100, size=(45, 25), key="-PBAR-"), sg.Button("Exit", key="-EXIT-", size=(7, 1)), sg.Button("Clear", size=(7, 1), key="-CLEAR_OUTPUT-", tooltip="Clears Output Window and Progressbar if stuck.")]]

    layout = [[sg.Column(column_description)],
              [sg.Column(column_file_save_location)],
              [sg.Column(column_download_layout)],
              [sg.Column(column_output_and_progressbar, justification="center")]]

    # ====== GUI Events ======#
    window = sg.Window("YouTube Downloader", layout, font="Arial 16", finalize=True, right_click_menu=MENU_RIGHT_CLICK)
    
    # Event loop to process "events" and get the "values" of the inputs
    while True:

        event, values = window.read()
        
        # Validate YouTube URL
        youtube_url = values["-LINK_INPUT-"] # GUI Link Input Element
        validate_youtube_url = (
                    r'(https?://)?(www\.)?'
                    '(youtube|youtu|youtube-nocookie)\.(com|be)/'
                    '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
                )
        valid_youtube_url = re.match(validate_youtube_url, youtube_url)
        
        # ----Closing the programm with either option [X] or just by pressing "Exit"----#
        if (event == sg.WIN_CLOSED or event == "-EXIT-"):
            break
        
        # Copy Paste Functionality (tk modifier, thanks to Mike from PSG)
        if event in ('Copy', 'Paste'):
            try:
                widget = window.find_element_with_focus().widget
                if event == 'Copy' and widget.select_present():
                    text = widget.selection_get()
                    window.TKroot.clipboard_clear()
                    window.TKroot.clipboard_append(text)
                elif event == 'Paste':
                    if widget.select_present():
                        widget.delete(sg.tk.SEL_FIRST, sg.tk.SEL_LAST)
                    widget.insert(sg.tk.INSERT, window.TKroot.clipboard_get())
            except Exception as e:
                window["-OUTPUT_WINDOW-"].update(f"ERROR: Something went wrong!\nError Message: {e}")
            
        if event == "-CHECK_IF_FFMPEG_INSTALLED-":
            try:
                result = subprocess.run(["ffmpeg", "-version"], capture_output=True) # Check if FFmpeg installed.
                if result.returncode == 0:
                    window["-OUTPUT_WINDOW-"].update("FFmpeg is installed.",text_color="#6dc151")
                elif result.returncode == 1:
                    window["-OUTPUT_WINDOW-"].update("FFmpeg is not installed.",text_color="#db4e44")
            except Exception as e:
                window["-OUTPUT_WINDOW-"].update(f"ERROR: Something went wrong!\nError Message: {e}")
            
        if event == "-BUTTON_DOWNLOAD-" and values["-DOWNLOAD_FORMAT-"] == "Video Format":
            try:
                window["-OUTPUT_WINDOW-"].update(text_color="#d2d2d3")
                if len(values["-LINK_INPUT-"]) == 0:
                    window["-OUTPUT_WINDOW-"].update(
                        "ERROR: Please enter a YouTube link for downloading.")
                elif not valid_youtube_url:
                    window["-OUTPUT_WINDOW-"].update("ERROR: Not a valid YouTube URL.")
                elif len(values["-SAVE_TO_FOLDER-"]) == 0:
                    window["-OUTPUT_WINDOW-"].update(
                        "ERROR: Please enter a path where to save downloads.")
                elif valid_youtube_url:
                    download_thread = threading.Thread(target=download_youtube_video, args=(values["-LINK_INPUT-"], values["-SAVE_TO_FOLDER-"], values["-QUALITY_FORMAT-"]))
                    download_thread.start()
            except Exception as e:
                window["-OUTPUT_WINDOW-"].update(f"ERROR: Something went wrong!\nError Message: {e}")

        if event == "-BUTTON_DOWNLOAD-" and values["-DOWNLOAD_FORMAT-"] == "Audio Format":
            try:
                window["-OUTPUT_WINDOW-"].update(text_color="#d2d2d3")
                if len(values["-LINK_INPUT-"]) == 0:
                    window["-OUTPUT_WINDOW-"].update("ERROR: Please enter a YouTube link for downloading.")
                elif not valid_youtube_url:
                    window["-OUTPUT_WINDOW-"].update("ERROR: Not a valid YouTube URL.")
                elif len(values["-SAVE_TO_FOLDER-"]) == 0:
                    window["-OUTPUT_WINDOW-"].update("ERROR: Please enter a path where to save downloads.")
                elif valid_youtube_url:
                    download_thread = threading.Thread(target=download_youtube_audio, args=(values["-LINK_INPUT-"], values["-SAVE_TO_FOLDER-"], values["-QUALITY_FORMAT-"]))
                    download_thread.start()
            except Exception as e:
                window["-OUTPUT_WINDOW-"].update(f"ERROR: Something went wrong!\nError Message: {e}")
                
        if event == "-STREAM_INFO_BUTTON-" and values["-DOWNLOAD_FORMAT-"] == "Video Format":
            try:
                window["-OUTPUT_WINDOW-"].update(text_color="#d2d2d3")
                if len(values["-LINK_INPUT-"]) == 0:
                  window["-OUTPUT_WINDOW-"].update("ERROR: Cannot get info of audio stream because link input is empty.")  
                elif not valid_youtube_url:
                    window["-OUTPUT_WINDOW-"].update("ERROR: Not a valid YouTube URL.")
                elif valid_youtube_url:
                    get_audio_stream_thread = threading.Thread(target=video_stream, args=(values["-LINK_INPUT-"],))
                    get_audio_stream_thread.start()
            except Exception as e:
                window["-OUTPUT_WINDOW-"].update(f"ERROR: Something went wrong!\nError Message: {e}")
        
        if event == "-STREAM_INFO_BUTTON-" and values["-DOWNLOAD_FORMAT-"] == "Audio Format":
            try:
                window["-OUTPUT_WINDOW-"].update(text_color="#d2d2d3")
                if len(values["-LINK_INPUT-"]) == 0:
                  window["-OUTPUT_WINDOW-"].update("ERROR: Cannot get info of audio stream because link input is empty.")  
                elif not valid_youtube_url:
                    window["-OUTPUT_WINDOW-"].update("ERROR: Not a valid YouTube URL.")
                elif valid_youtube_url:
                    get_audio_stream_thread = threading.Thread(target=audio_stream, args=(values["-LINK_INPUT-"],))
                    get_audio_stream_thread.start()
            except Exception as e:
                window["-OUTPUT_WINDOW-"].update(f"ERROR: Something went wrong!\nError Message: {e}")

        if event == "-URL_REDIRECT-":
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z"
            webbrowser.open(url)

        if event == "-CLEAR_OUTPUT-":
            window["-OUTPUT_WINDOW-"].update("")
            window["-PBAR-"].update(0)
            
        if event == "Clear Output":
            window["-OUTPUT_WINDOW-"].update("")

        if event == "Version":
            sg.popup_scrolled(sg.get_versions())

    window.close()

if __name__ == '__main__':
    main()