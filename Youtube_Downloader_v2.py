import PySimpleGUI as sg
from pytube import YouTube
import threading

# ====== Functions ======#


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

        if len(values["-QUALITY_FORMAT-"]) != 0 and values["-DOWNLOAD_FORMAT-"] == "Video Format":
            window["-BUTTON_DOWNLOAD-"].update(disabled=True)
            window["-STREAM_INFO_BUTTON-"].update(disabled=True)
            window["-OUTPUT_WINDOW-"].print("Starting download... please wait.\n")
            yt = YouTube(YouTubeURL, use_oauth=False, allow_oauth_cache=True,on_progress_callback=progress_callback)

            video = yt.streams.get_by_resolution(values["-QUALITY_FORMAT-"])
            video.download(output_path=output_path, skip_existing=True)
            window["-OUTPUT_WINDOW-"].update(f"{yt.title} (Quality: {video.resolution})\nhas been successfully downloaded.\nSaved in {output_path}")
            window["-BUTTON_DOWNLOAD-"].update(disabled=False)
            window["-STREAM_INFO_BUTTON-"].update(disabled=False)
            window["-PBAR-"].update(0)
        else:
            window["-OUTPUT_WINDOW-"].update("ERROR: Select a Quality of Stream first.")

    except Exception as e:
        window["-OUTPUT_WINDOW-"].update("")
        window["-OUTPUT_WINDOW-"].print(f"ERROR: {e}")
        window["-BUTTON_DOWNLOAD-"].update(disabled=False)


def download_youtube_audio(YouTubeURL, output_path):
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

        if values["-DOWNLOAD_FORMAT-"] == "Audio Format":
            window["-STREAM_INFO_BUTTON-"].update(disabled=True)
            window["-OUTPUT_WINDOW-"].print("Starting download... please wait.\n")
            yt = YouTube(YouTubeURL, use_oauth=False, allow_oauth_cache=True,
                         on_progress_callback=progress_callback)

            # Gets highest bitrate for audio automatically. I guess this should be the default as you want the highest avaiable quality, especially for downloading music. :)
            music = yt.streams.get_audio_only()
            music.download(output_path=output_path, skip_existing=True)
            window["-OUTPUT_WINDOW-"].update(f"{yt.title} (Quality: {music.abr})\nhas been successfully downloaded.\nSaved in {output_path}")
            window["-BUTTON_DOWNLOAD-"].update(disabled=False)
            window["-STREAM_INFO_BUTTON-"].update(disabled=False)
            window["-PBAR-"].update(0)

    except Exception as e:
        window["-OUTPUT_WINDOW-"].update("")
        window["-OUTPUT_WINDOW-"].print(f"ERROR: {e}")
        window["-BUTTON_DOWNLOAD-"].update(disabled=False)
        window["-STREAM_INFO_BUTTON-"].update(disabled=False)


def video_stream(YouTubeURL):
    yt = YouTube(YouTubeURL)
    window["-OUTPUT_WINDOW-"].update(f"Video Title: {yt.title}")
    window["-OUTPUT_WINDOW-"].print("\nAvailable Video Streams: Loading... please wait.")
    video_streams = yt.streams.filter(only_video=True, subtype="mp4")
    # Collect resolutions in a list
    resolutions = [stream.resolution for stream in video_streams]
    for stream in video_streams:
        window["-OUTPUT_WINDOW-"].update(
            f"Resolution: {stream.resolution}, Codec: {stream.subtype}, Filesize: {stream.filesize / (1024 * 1024):.2f} MB")
    window["-QUALITY_FORMAT-"].update(values=resolutions)

# def audio_stream(YouTubeURL):
#    yt = YouTube(YouTubeURL)
#    window["-OUTPUT_WINDOW-"].update(f"Video Title: {yt.title}")
#    window["-OUTPUT_WINDOW-"].print("Available Audio Streams: Loading... please wait.")
#    audio_streams = yt.streams.filter(only_audio=True, progressive=False)
#    abrs = [stream.abr for stream in audio_streams]  # Collect audio quality (abr) in a list
#    for stream in audio_streams:
#        window["-OUTPUT_WINDOW-"].print(f"Abr: {stream.abr}, Filesize: {stream.filesize / (1024 * 1024):.2f} MB")
#        window["-QUALITY_FORMAT-"].update(values=abrs)


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

# ====== GUI LAYOUT ======#
column_description = [[sg.Text("YouTube Downloader", font="Arial 20 bold underline", text_color="#c63a3d")],
                      [sg.Text("A YouTube Downloader built with Python and PySimpleGUI.")],
                      [sg.Text("Where to save", font="Arial 16 bold underline", text_color="#c63a3d")],
                      [sg.Text("Choose a location where you want to save the Files")],
                      [sg.Text("Save File to:"), sg.Input(key="-SAVE_TO_FOLDER-"), sg.FolderBrowse(size=(10, 1))]]

column_download_layout = [[sg.Text("Downloading Part", font="Arial 16 bold underline", text_color="#c63a3d")],
                          [sg.Text("Stream type and quality settings:")],
                          [sg.Text("Type of stream to download:   "), sg.Combo(["Audio Format", "Video Format"],default_value="Audio Format", readonly=True, enable_events=True, key="-DOWNLOAD_FORMAT-")],
                          [sg.Text("Quality of stream to download:"), sg.Combo("", key="-QUALITY_FORMAT-", size=(13, 1))],
                          [sg.Text("Add a 'https://www.youtube.com/' link in the input box below:")],
                          [sg.Text("Enter URL Link"), sg.Input(key="-LINK_INPUT-", size=(33, 1)), sg.Button("Download", key="-BUTTON_DOWNLOAD-"), sg.Button("Stream Info", key="-STREAM_INFO_BUTTON-")]]


column_output_and_progressbar = [[sg.Multiline(size=(65, 10), key="-OUTPUT_WINDOW-")],
                                 [sg.Text("Progress:"), sg.ProgressBar(100, size=(45, 25), key="-PBAR-"), sg.Button("Exit", key="-EXIT-", size=(7, 1)), sg.Button("Clear", size=(7, 1), key="-CLEAR_OUTPUT-", tooltip="Clears Output Window and Progressbar if stuck.")]]

layout = [[sg.Column(column_description, justification="center")],
          [sg.Column(column_download_layout)],
          [sg.Column(column_output_and_progressbar, justification="center")]]

# ====== GUI Events ======#
window = sg.Window("YouTube Downloader", layout,
                   font="Arial 16", finalize=True)

# Event loop to process "events" and get the "values" of the inputs
while True:

    event, values = window.read()

    # ----Closing the programm with either option the [X] or just by pressing "Exit"----#
    if (event == sg.WIN_CLOSED or event == "-EXIT-"):
        break

    if event == "-BUTTON_DOWNLOAD-" and values["-DOWNLOAD_FORMAT-"] == "Video Format":
        if len(values["-SAVE_TO_FOLDER-"]) == 0:
            window["-OUTPUT_WINDOW-"].update(
                "ERROR: Please enter a path where to save to the downloaded file.")
        elif len(values["-LINK_INPUT-"]) == 0:
            window["-OUTPUT_WINDOW-"].update(
                "ERROR: Please enter a YouTube link for Video Download.")
        else:
            download_thread = threading.Thread(target=download_youtube_video, args=(
                values["-LINK_INPUT-"], values["-SAVE_TO_FOLDER-"]))
            download_thread.start()

    elif event == "-BUTTON_DOWNLOAD-" and values["-DOWNLOAD_FORMAT-"] == "Audio Format":
        if len(values["-SAVE_TO_FOLDER-"]) == 0:
            window["-OUTPUT_WINDOW-"].update(
                "ERROR: Please enter a path where to save to the downloaded file.")
        elif len(values["-LINK_INPUT-"]) == 0:
            window["-OUTPUT_WINDOW-"].update(
                "ERROR: Please enter a YouTube link for Audio Download.")
        else:
            download_thread = threading.Thread(target=download_youtube_audio, args=(
                values["-LINK_INPUT-"], values["-SAVE_TO_FOLDER-"]))
            download_thread.start()

    elif event == "-STREAM_INFO_BUTTON-" and values["-DOWNLOAD_FORMAT-"] == "Video Format":
        if len(values["-LINK_INPUT-"]) > 0:
            get_video_stream_thread = threading.Thread(
                target=video_stream, args=(values["-LINK_INPUT-"],))
            get_video_stream_thread.start()
        else:
            window["-OUTPUT_WINDOW-"].update(
                "ERROR: Cannot get info of video stream because input is empty.")

    # elif event == "-STREAM_INFO_BUTTON-" and values["-DOWNLOAD_FORMAT-"] == "Audio Format":
    #   if len(values["-LINK_INPUT-"]) > 0:
    #       get_audio_stream_thread = threading.Thread(target=audio_stream, args=(values["-LINK_INPUT-"],))
    #       get_audio_stream_thread.start()
    #   else:
    #       window["-OUTPUT_WINDOW-"].print("ERROR: Cannot get info of Audio Stream because input is empty.")

    elif event == "-CLEAR_OUTPUT-":
        window["-OUTPUT_WINDOW-"].update("")
        window["-PBAR-"].update(0)

window.close()
