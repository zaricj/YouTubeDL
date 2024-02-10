from PIL import Image, ImageTk
from urllib import request
import PySimpleGUI as sg
from pytube import YouTube

url = "https://www.youtube.com/watch?v=ACNgFW50EbU"
yt = YouTube(url)

thumbnail = yt.thumbnail_url

# Get one PNG file from website and save to file
url = thumbnail
headers = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36')}
req = request.Request(thumbnail, headers=headers)
response = request.urlopen(req)
if response.status != 200:
    print("Failed to load image from website !")
    exit()
data = response.read()

filename = "example.png"
with open(filename, "wb") as f:
    f.write(data)

# Resize PNG file to size (300, 300)
size = (600, 600)
im = Image.open(filename)
im = im.resize(size, resample=Image.BICUBIC)

sg.theme('DarkGreen3')

layout = [
    [sg.Image(size=(600, 600), key='-IMAGE-')],
]
window = sg.Window('Window Title', layout, margins=(0, 0), finalize=True)

# Convert im to ImageTk.PhotoImage after window finalized
image = ImageTk.PhotoImage(image=im)

# update image in sg.Image
window['-IMAGE-'].update(data=image)

while True:

    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

window.close()