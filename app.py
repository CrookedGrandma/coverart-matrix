import json
import numpy as np
import os
import requests
import socketserver
import spotipy
import time
import threading
from configparser import ConfigParser
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect
from io import BytesIO
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from spotipy import SpotifyOAuth
from PIL import Image
from urllib.parse import urlencode

load_dotenv()
scope = "user-read-currently-playing"
getstatusurl = "https://web.djkhas.com/coverart/getstatus.php"
setstatusurl = "https://web.djkhas.com/coverart/setstatus.php"
headers = {"User-Agent": "Mozilla/5.0"}

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, open_browser=False))


def setstatus(prop, value):
    requests.post(setstatusurl, headers=headers, json={
        'property': prop,
        'value': value,
    })

def screen_off():
    matrix.SwapOnVSync(matrix.CreateFrameCanvas())

def black_screen():
    return np.zeros((matrix.width, matrix.height, 3))

def get_img(currentimgurl, currentimgarray):
    track = sp.current_user_playing_track()
    if track is None:
        return None, black_screen()
    url = track["item"]["album"]["images"][0]["url"]
    if url == currentimgurl:
        return currentimgurl, currentimgarray
    img = Image.open(BytesIO(requests.get(url).content))
    img.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
    img = img.convert("RGB")
    array = np.array(img)
    return url, array

def check_login():
    auth = sp.auth_manager
    token = auth.validate_token(auth.cache_handler.get_cached_token())
    if token is not None:
        if auth.is_token_expired(token):
            auth.refresh_access_token(token["refresh_token"])
        return True
    return False

class MyTCP(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # handle requests
        if self.data.startswith(b"LOGIN"):
            if check_login():
                self.request.sendall(bytes(f"CACHED:{sp.me()['display_name']}", "utf-8"))
            else:
                url = sp.auth_manager.get_authorize_url()
                self.request.sendall(bytes(url, "utf-8"))
        elif self.data.startswith(b"REDIR"):
            url = self.data.split(b":", 1)[1].decode("utf-8")
            try:
                code = sp.auth_manager.parse_response_code(url)
                sp.auth_manager.get_access_token(code, as_dict=False)
                if check_login():
                    self.request.sendall(bytes(str(f"LOGGEDIN:{sp.me()['display_name']}"), "utf-8"))
                else:
                    self.request.sendall(b"login failed: login not set")
            except spotipy.SpotifyOauthError as e:
                self.request.sendall(bytes(f"login failed: {e.error_description}", "utf-8"))
        else:
            self.request.sendall(b"wrong request")


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCP)

    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 32
    matrix = RGBMatrix(options=options)
    offset_canvas = matrix.CreateFrameCanvas()

    interval = 5.0

    currentBrightness = 100
    currentImgUrl = None
    currentImgArray = None

    try:
        starttime = time.time()
        while True:
            try:
                print("tick")
                status = json.loads(requests.get(getstatusurl, headers=headers).text)
                if status["req_login"] > 0:
                    # Login
                    print("Login request")
                    setstatus("req_login", "0")
                    print("Waiting for login prompt...")
                    server.handle_request()
                    if not check_login():
                        print("Waiting for return code...")
                        server.handle_request()
                    screen_off()
                elif status["req_login"] < 0:
                    # Logout
                    print("Logout request")
                    setstatus("req_login", "0")
                    if os.path.exists(".cache"):
                        os.remove(".cache")
                    screen_off()
                elif status["power"] == "on":
                    # Power on
                    print("Power on")
                    currentImgUrl, currentImgArray = get_img(currentImgUrl, currentImgArray)
                    px = currentImgArray
                    newBrightness = status["brightness"]
                    if newBrightness != currentBrightness:
                        currentBrightness = newBrightness
                        print(f"Setting brightness to {currentBrightness}")
                        matrix.brightness = currentBrightness
                    for x in range(0, matrix.width):
                        for y in range(0, matrix.height):
                            offset_canvas.SetPixel(matrix.width - x, y, px[x, y, 0], px[x, y, 1], px[x, y, 2])
                    offset_canvas = matrix.SwapOnVSync(offset_canvas)
                else:
                    # Power off
                    print("Power off")
                    screen_off()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"Skipping tick -- error found: {e}")
                screen_off()
            time.sleep(interval - ((time.time() - starttime) % interval))
    except KeyboardInterrupt:
        screen_off()
        server.server_close()
        print("Program exited.")
