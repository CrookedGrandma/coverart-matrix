import numpy as np
import os
import requests
import spotipy
import time
import threading
from configparser import ConfigParser
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect
from io import BytesIO
# from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
from urllib.parse import urlencode

load_dotenv()
scope = "user-read-currently-playing"
headers = {"User-Agent": "Mozilla/5.0"}


def screen_off(mat):
    mat.SwapOnVSync(mat.CreateFrameCanvas())

def get_img():
    raise NotImplementedError()


options = RGBMatrixOptions()
options.rows = 32
options.cols = 32
options.brightness = 100
matrix = RGBMatrix(options=options)
offset_canvas = matrix.CreateFrameCanvas()


try:
    while True:
        power = requests.get("https://web.djkhas.com/coverart/getpower.php", headers=headers).text
        if power == "on":
            # px = get_img()
            for x in range(0, matrix.width):
                for y in range(0, matrix.height):
                    # offset_canvas.SetPixel(x, y, px[x, y, 0], px[x, y, 1], px[x, y, 2])
                    offset_canvas.SetPixel(x, y, 255, 0, 0)
            offset_canvas = matrix.SwapOnVSync(offset_canvas)
        else:
            screen_off(matrix)
        time.sleep(5)
except KeyboardInterrupt:
    screen_off(matrix)
    print("Program exited.")
