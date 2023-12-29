import PySimpleGUI as sg
from pytube import YouTube
import threading
import subprocess
import os
import ffmpeg
import re
import webbrowser
from pathlib import Path


def main():

    # Add the FFmpeg binary directory to the PATH
    ffmpeg_path = "./ffmpeg/bin"
    os.environ["PATH"] += os.pathsep + os.path.abspath(ffmpeg_path)

    # ====== Functions ====== #
    def download_youtube_video(youtube_urls, output_path, chosen_resolution):
        counter = 0
        for yt_urls in youtube_urls:
            counter += 1
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
                    window["-OUTPUT_WINDOW-"].update(
                        "Starting download and encoding... please wait.\n")

                    yt = YouTube(yt_urls, use_oauth=False, allow_oauth_cache=True,
                                 on_progress_callback=progress_callback)

                    # Filter video streams based on the chosen resolution and audio for getting the videos audio for later merging with FFmpeg
                    video_streams = yt.streams.filter(
                        only_video=True, mime_type="video/mp4", res=chosen_resolution)
                    # Get the highest quality audio stream of the video (128kbps)
                    audio_streams = yt.streams.get_audio_only("mp4")

                    # Find the first available stream with the chosen video quality
                    chosen_video_stream = next(
                        (stream for stream in video_streams if stream.resolution == chosen_resolution), None)

                    # Check if there is at least one stream with the chosen resolution
                    if video_streams:

                        # Forbidden characters pattern in filename (Windows)
                        forbidden_chars_pattern = r'[\\/:"?<>|]'

                        # Sanitized filename for ffmpeg encoder
                        sanitized_filename = yt.title.replace(" ", "_")
                        sanitized_filename_with_extension = f"{sanitized_filename}.{chosen_video_stream.subtype}"

                        # If the filename contains forbidden characters, delete them for VIDEO
                        if re.search(forbidden_chars_pattern, sanitized_filename_with_extension):
                            cleared_video_filename = re.sub(
                                forbidden_chars_pattern, '', sanitized_filename_with_extension)
                        else:
                            cleared_video_filename = sanitized_filename_with_extension

                        # Download the selected video and audio stream
                        chosen_video_stream.download(
                            output_path=output_path, filename=cleared_video_filename, skip_existing=True)
                        audio_streams.download(
                            output_path=output_path, filename="audio.mp4", skip_existing=True)

                        # FFmpeg paths for the files
                        # The Downloaded video file
                        the_video_file = os.path.join(
                            output_path, cleared_video_filename)
                        # The Downloaded audio file
                        the_audio_file = os.path.join(output_path, "audio.mp4")
                        encoded_finished_filename = os.path.join(
                            output_path, "encoded_video_with_audio.mp4")  # Encoded File (merge audo/video)

                        # FFmpeg extract audio and add it to the downlaoded video
                        subprocess.run(
                            f"ffmpeg -i {the_video_file} -i {the_audio_file} -c copy {encoded_finished_filename}")

                        # Remove the downloaded audio file "audio.mp4"
                        os.remove(the_audio_file)
                        # Remove the downloaded audio file "yt.title.mp4"
                        os.remove(the_video_file)
                        # Rename the concatenated file to the original video file name
                        os.rename(encoded_finished_filename, the_video_file)
                        # Replace underscore (_) with whitespaces again for the encoded file
                        replace_with_whitespaces = the_video_file.replace(
                            "_", " ")
                        os.rename(the_video_file, replace_with_whitespaces)

                        window["-OUTPUT_WINDOW-"].update(
                            f"Links have been successfully downloaded and converted to MP3.\nSaved in {output_path}")
                    else:
                        window["-OUTPUT_WINDOW-"].update(
                            f"No video stream found with resolution: {chosen_resolution}\nPerhaps it's the wrong format?\nIf so, press Stream Info button again to reload the list.")

                    window["-BUTTON_DOWNLOAD-"].update(disabled=False)
                    window["-STREAM_INFO_BUTTON-"].update(disabled=False)
                    window["-PBAR-"].update(0)
                else:
                    window["-OUTPUT_WINDOW-"].update(
                        "ERROR: Select a Quality of Stream first.")
                    window["-BUTTON_DOWNLOAD-"].update(disabled=False)
                    window["-STREAM_INFO_BUTTON-"].update(disabled=False)
                    window["-PBAR-"].update(0)
            except Exception as e:
                window["-OUTPUT_WINDOW-"].update("")
                window["-OUTPUT_WINDOW-"].print(f"ERROR: {e}")
                window["-BUTTON_DOWNLOAD-"].update(disabled=False)
                window["-STREAM_INFO_BUTTON-"].update(disabled=False)
                window["-PBAR-"].update(0)

    def download_youtube_audio(youtube_urls, output_path, chosen_audio_quality):
        counter = 0
        for yt_urls in youtube_urls:
            counter = + 1
            try:
                window["-STREAM_INFO_BUTTON-"].update(disabled=True)
                window["-BUTTON_DOWNLOAD-"].update(disabled=True)
                window["-PBAR-"].update(0)
                window["-OUTPUT_WINDOW-"].update("")

                def progress_callback(stream, chunk, remaining_bytes):
                    total_size = stream.filesize
                    bytes_downloaded = total_size - remaining_bytes
                    percentage = (bytes_downloaded / total_size) * 100
                    # progress_text = f"Downloaded {bytes_downloaded}/{total_size}\n"
                    window["-PBAR-"].update(percentage)

                if len(chosen_audio_quality) != 0:
                    window["-STREAM_INFO_BUTTON-"].update(disabled=True)
                    window["-OUTPUT_WINDOW-"].update(
                        f"Starting download and ffmpeg encoder for index: {counter} link... please wait.\n")
                    yt = YouTube(yt_urls, use_oauth=False, allow_oauth_cache=True,
                                 on_progress_callback=progress_callback)

                    # Filter audio streams based on the chosen quality
                    audio_streams = yt.streams.filter(
                        only_audio=True, audio_codec="opus")

                    # Find the first available stream with the chosen audio quality
                    chosen_audio_stream = next(
                        (stream for stream in audio_streams if stream.abr == chosen_audio_quality), None)

                    if chosen_audio_stream:

                        # Forbidden characters in filename pattern
                        forbidden_chars_pattern = r'[\\/:"?<>|]'

                        # Sanitize the filename by replacing spaces with underscores
                        sanitized_filename = yt.title.replace(" ", "_")
                        sanitized_filename_with_extension = sanitized_filename + \
                            "." + chosen_audio_stream.subtype

                        # If the filename contains forbidden characters, delete them in an if clause
                        if re.search(forbidden_chars_pattern, sanitized_filename_with_extension):
                            cleared_video_filename = re.sub(
                                forbidden_chars_pattern, '', sanitized_filename_with_extension)
                        else:
                            cleared_video_filename = sanitized_filename_with_extension
                        cleared_filename_without_extension = cleared_video_filename.removesuffix(
                            f".{chosen_audio_stream.subtype}")

                        # Download the chosen audio stream
                        chosen_audio_stream.download(
                            output_path=output_path, filename=cleared_video_filename, skip_existing=True)

                        # FFmpeg conversion to MP3
                        input_file = os.path.join(
                            output_path, cleared_video_filename)
                        output_file = os.path.join(
                            output_path, f"{cleared_filename_without_extension}.mp3")
                        subprocess.run(['ffmpeg', '-i', input_file, '-vn', '-ar', '44100',
                                       '-ac', '2', '-b:a', '192k', output_file], capture_output=True)
                        os.remove(input_file)

                        # Replace underscore (_) with whitespaces again for the encoded file
                        replace_with_whitespaces = output_file.replace(
                            "_", " ")
                        os.rename(output_file, replace_with_whitespaces)

                        window["-OUTPUT_WINDOW-"].update(
                            f"Links have been successfully downloaded and converted to MP3.\nSaved in {output_path}")
                    else:
                        window["-OUTPUT_WINDOW-"].update(
                            f"No audio stream found with quality: {chosen_audio_quality}\nPerhaps it's the wrong format?\nIf so, press Stream Info button again to reload the list.")

                    # Uncomment later?
                    window["-BUTTON_DOWNLOAD-"].update(disabled=False)
                    window["-STREAM_INFO_BUTTON-"].update(disabled=False)
                    window["-PBAR-"].update(0)
                else:
                    window["-OUTPUT_WINDOW-"].update(
                        "ERROR: Select a Quality of Stream first.")
                    window["-BUTTON_DOWNLOAD-"].update(disabled=False)
                    window["-STREAM_INFO_BUTTON-"].update(disabled=False)
                    window["-PBAR-"].update(0)
            except Exception as e:
                window["-OUTPUT_WINDOW-"].update("")
                window["-OUTPUT_WINDOW-"].print(f"ERROR: {e}")
                window["-BUTTON_DOWNLOAD-"].update(disabled=False)
                window["-STREAM_INFO_BUTTON-"].update(disabled=False)
                window["-PBAR-"].update(0)

    def video_stream(youtube_urls):
        try:
            window["-BUTTON_DOWNLOAD-"].update(disabled=True)
            window["-STREAM_INFO_BUTTON-"].update(disabled=True)
            yt = YouTube(youtube_urls)
            window["-OUTPUT_WINDOW-"].update("Available Video Streams:\n")
            # Filter streams and exclude those with video_codec=None
            video_streams = [stream for stream in yt.streams.filter(
                only_video=True, mime_type="video/mp4")]
            # Collect resolutions in a list
            resolutions = [stream.resolution for stream in video_streams]
            for stream in video_streams:
                window["-OUTPUT_WINDOW-"].print(
                    f"Resolution: {stream.resolution},  FPS: {stream.fps}, Codec: {stream.subtype}, Filesize: {stream.filesize / (1024 * 1024):.2f} MB")
                window["-QUALITY_FORMAT-"].update(values=resolutions)
            window["-BUTTON_DOWNLOAD-"].update(disabled=False)
            window["-STREAM_INFO_BUTTON-"].update(disabled=False)
        except Exception as e:
            window["-OUTPUT_WINDOW-"].update(f"ERROR: {e}")
            window["-BUTTON_DOWNLOAD-"].update(disabled=False)
            window["-STREAM_INFO_BUTTON-"].update(disabled=False)

    def audio_stream(youtube_urls):
        try:
            window["-BUTTON_DOWNLOAD-"].update(disabled=True)
            window["-STREAM_INFO_BUTTON-"].update(disabled=True)
            yt = YouTube(youtube_urls)
            window["-OUTPUT_WINDOW-"].update("Available Audio Streams:\n")
            audio_streams = yt.streams.filter(
                only_audio=True, audio_codec="opus")
            # Collect audio quality (abr) in a list
            abrs = [stream.abr for stream in audio_streams]
            for stream in audio_streams:
                window["-QUALITY_FORMAT-"].update(values=abrs)
                window["-OUTPUT_WINDOW-"].print(
                    f"Abr: {stream.abr}, Codec: {stream.subtype}, Filesize: {stream.filesize / (1024 * 1024):.2f} MB")
            window["-BUTTON_DOWNLOAD-"].update(disabled=False)
            window["-STREAM_INFO_BUTTON-"].update(disabled=False)
        except Exception as e:
            window["-OUTPUT_WINDOW-"].update(f"ERROR: {e}")
            window["-BUTTON_DOWNLOAD-"].update(disabled=False)
            window["-STREAM_INFO_BUTTON-"].update(disabled=False)

    # Function to check for duplicate links
    def is_duplicate(url):
        return url in urls

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

    MENU_RIGHT_CLICK = ["", ["Clear Output", "Version", "Exit"]]
    # Create right click menu for input field
    right_click_menu_input_field = ["&Right", ["&Copy", "&Paste"]]
    right_click_listbox = ["&Right", ["&Delete", "&Delete All"]]

    # ====== GUI LAYOUT ====== #
    column_description = [[sg.Text("YouTube Downloader", font="Arial 20 bold underline", text_color="#c63a3d")],
                          [sg.Text(
                              "A YouTube Downloader built with Python and PySimpleGUI.")],
                          [sg.Text("FFmpeg is required! You can get in here:"), sg.Text("FFmpeg", font="Arial 14 underline", text_color="#c63a3d", enable_events=True, tooltip="Direct link download to FFmpeg.", key="-URL_REDIRECT-")]]

    column_file_save_location = [[sg.Text("Where to save", font="Arial 16 bold underline", text_color="#c63a3d")],
                                 [sg.Text(
                                     "Choose a location where you want to save downloads:")],
                                 [sg.Text("Save Location:"), sg.Input(size=(40, 1), key="-SAVE_TO_FOLDER-"), sg.FolderBrowse(size=(10, 1))]]

    column_download_layout = [[sg.Text("Downloading Part", font="Arial 16 bold underline", text_color="#c63a3d")],
                              [sg.Text("Stream type and quality settings:")],
                              [sg.Text("Type of stream to download:   "), sg.Combo(["Audio Format", "Video Format"],
                                                                                   default_value="Audio Format", readonly=True, enable_events=True, key="-DOWNLOAD_FORMAT-")],
                              [sg.Text("Quality of stream to download:"), sg.Combo(
                                  "", readonly=True, key="-QUALITY_FORMAT-", size=(13, 1))],
                              [sg.Text(
                                  "Add a 'https://www.youtube.com/' link in the input box below:")],
                              [sg.Text("Enter URL:"), sg.Input(key="-LINK_INPUT-", size=(31, 1), right_click_menu=right_click_menu_input_field), sg.Button("+", size=(3, 1), key="-APPEND_URL_TO_LIST-"), sg.Button("Download", key="-BUTTON_DOWNLOAD-"), sg.Button("Stream Info", key="-STREAM_INFO_BUTTON-")]]

    column_output_and_progressbar = [[sg.Listbox(values=[], size=(65, 6), key='-URL_LIST-', right_click_menu=right_click_listbox)],
                                     [sg.HSeparator()],
                                     [sg.Multiline(
                                         size=(65, 8), key="-OUTPUT_WINDOW-")],
                                     [sg.Text("Progress:"), sg.ProgressBar(100, size=(40, 25), key="-PBAR-"), sg.Text("List Size:"), sg.StatusBar(text="0", size=(4, 1), key="-STATUSBAR-"), sg.Button("Clear", size=(6, 1), key="-CLEAR_OUTPUT-", tooltip="Clears Output Window and Progressbar if stuck.")]]

    layout = [[sg.Column(column_description)],
              [sg.Column(column_file_save_location)],
              [sg.Column(column_download_layout)],
              [sg.Column(column_output_and_progressbar, justification="center")]]

    # ====== GUI Events ======#
    window = sg.Window("YouTube Downloader | Credit: Jovan Zaric", layout,
                       font="Arial 16", finalize=True, right_click_menu=MENU_RIGHT_CLICK)

    # Variables
    urls = []  # List to store YouTube URLs
    id_counter = 1  # ID counter to add to listbox

    # Event loop to process "events" and get the "values" of the inputs
    while True:

        event, values = window.read()

        # Closing the programm with either option [X] or just by pressing "Exit"
        if (event == sg.WIN_CLOSED or event == "-EXIT-"):
            break

        # Delete and Delete All functionality with right click per item in list (needs to be selected with left click first)
        if event in ("Delete", "Delete All"):
            if event == "Delete":
                selected_indices = window["-URL_LIST-"].get_indexes()
                for index in selected_indices:
                    yt = YouTube(urls[index])
                    title = yt.title
                    urls.pop(index)
                    id_counter -= 1
                    window["-URL_LIST-"].update(values=urls)
                window["-OUTPUT_WINDOW-"].print(len(urls))
                window["-STATUSBAR-"].update(len(urls))
                window["-OUTPUT_WINDOW-"].update(
                    f"Removed `{title}` from list!")
            elif event == "Delete All":
                urls = []
                id_counter = 1
                window["-URL_LIST-"].update(values=urls)
                window["-STATUSBAR-"].update("0")
                window["-OUTPUT_WINDOW-"].update(
                    "Deleted whole List of links!")

        # Copy Paste Functionality (tk modifier, thanks to Mike from PSG)
        if event in ('Copy', 'Paste'):
            widget = window.find_element_with_focus().widget
            if event == 'Copy' and widget.select_present():
                text = widget.selection_get()
                window.TKroot.clipboard_clear()
                window.TKroot.clipboard_append(text)
            elif event == 'Paste':
                if widget.select_present():
                    widget.delete(sg.tk.SEL_FIRST, sg.tk.SEL_LAST)
                widget.insert(sg.tk.INSERT, window.TKroot.clipboard_get())

        # Append URLS to list and updating PySimpleGUI's ListBox
        elif event == "-APPEND_URL_TO_LIST-":
            url = values["-LINK_INPUT-"]
            if "https://www.youtube.com/watch" not in url:
                window["-OUTPUT_WINDOW-"].update(
                    "ERROR: Please enter a valid YouTube URL and not some trash.")
            elif url and not is_duplicate(url):
                urls.append(f"{id_counter}. {url}")
                id_counter += 1
                window['-URL_LIST-'].update(values=urls)
                window["-STATUSBAR-"].update(len(urls))
                window['-LINK_INPUT-'].update("")
                window["-OUTPUT_WINDOW-"].update("")
                yt = YouTube(url)
                window["-OUTPUT_WINDOW-"].print(
                    f"Added YouTube Video to list: {yt.title}")
            elif is_duplicate(url):
                window["-OUTPUT_WINDOW-"].update(
                    f"Duplicate link: '{url}' already in the list!")
                window["-LINK_INPUT"].update("")

        # Downloading Video File
        elif event == "-BUTTON_DOWNLOAD-" and values["-DOWNLOAD_FORMAT-"] == "Video Format":
            if len(values["-SAVE_TO_FOLDER-"]) == 0:
                window["-OUTPUT_WINDOW-"].update(
                    "ERROR: Please enter a path where to save the video download.")
            elif len(urls) == 0:
                window["-OUTPUT_WINDOW-"].update(
                    "ERROR. You haven't added any links for downloading, add a link to the input and press the + button.")
            else:
                window.perform_long_operation(lambda: download_youtube_video(
                    urls, values["-SAVE_TO_FOLDER-"], values["-QUALITY_FORMAT-"]), "-OUTPUT_WINDOW-")

        # Downloading Audio File
        elif event == "-BUTTON_DOWNLOAD-" and values["-DOWNLOAD_FORMAT-"] == "Audio Format":

            if len(values["-SAVE_TO_FOLDER-"]) == 0:
                window["-OUTPUT_WINDOW-"].update(
                    "ERROR: Please enter a path where to save the audio download.")
            elif len(urls) == 0:
                window["-OUTPUT_WINDOW-"].update(
                    "ERROR. You haven't added any links for downloading, add a link to the input and press the + button.")
            else:
                window.perform_long_operation(lambda: download_youtube_audio(
                    urls, values["-SAVE_TO_FOLDER-"], values["-QUALITY_FORMAT-"]), "-OUTPUT_WINDOW-")

        # Get Stream Info of YouTube Link for Video Downloading
        if event == "-STREAM_INFO_BUTTON-" and values["-DOWNLOAD_FORMAT-"] == "Video Format":
            if len(urls) != 0:
                get_video_stream_thread = threading.Thread(
                    target=video_stream, args=(urls[0],))
                get_video_stream_thread.start()
            else:
                window["-OUTPUT_WINDOW-"].update(
                    "ERROR: Listbox is empty, add links to it and try again.")

         # Get Stream Info of YouTube Link for Audio Downloading
        if event == "-STREAM_INFO_BUTTON-" and values["-DOWNLOAD_FORMAT-"] == "Audio Format":
            if len(urls) != 0:
                get_audio_stream_thread = threading.Thread(
                    target=audio_stream, args=(urls[0],))
                get_audio_stream_thread.start()
            else:
                window["-OUTPUT_WINDOW-"].update(
                    "ERROR: Listbox is empty, add links to it and try again.")

        if event == "-URL_REDIRECT-":
            url_ffmpeg = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z"
            webbrowser.open(url_ffmpeg)

        if event == "-CLEAR_OUTPUT-":
            window["-OUTPUT_WINDOW-"].update("")
            window["-PBAR-"].update(0)

        elif event == "Clear Output":
            window["-OUTPUT_WINDOW-"].update("")

        elif event == "Version":
            sg.popup_scrolled(sg.get_versions())

    window.close()


if __name__ == '__main__':
    main()
