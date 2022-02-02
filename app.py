import numpy as np
import os
import spotipy
import time
import threading
from configparser import ConfigParser
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
from urllib.parse import urlencode

load_dotenv()
app = Flask(__name__)

cfgfile = "config.ini"
cfg = ConfigParser()
cfg.read(cfgfile)
d = "DEFAULT"
dcfg = cfg[d]


def write_cfg(name, val):
    cfg.set(d, name, val)
    with open(cfgfile, "w") as configfile:
        cfg.write(configfile)
        configfile.close()


def test_sp_connection():
    global sp
    try:
        sp.me()
    except spotipy.exceptions.SpotifyException:
        write_cfg("token", "")
        sp = None


scope = "user-read-currently-playing"
sp = None
if dcfg["token"] != "":
    sp = spotipy.Spotify(auth=dcfg["token"])
    test_sp_connection()


class RGBHandler:
    def __init__(self):
        self.matrix = None
        self.rgb_thread = None
        self.alive = False
        self.options = dict(brightness=100, power=True)

    def _start_rgb(self, brightness):
        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 32
        if brightness is None:
            options.brightness = self.options["brightness"]
        else:
            options.brightness = brightness
            self.options["brightness"] = brightness
        self.matrix = RGBMatrix(options=options)
        img = Image.open("testimg2.png")
        img.thumbnail((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
        img = img.convert("RGB")
        px = np.array(img)
        offset_canvas = self.matrix.CreateFrameCanvas()
        self.alive = True
        while self.alive:
            for x in range(0, self.matrix.width):
                for y in range(0, self.matrix.height):
                    offset_canvas.SetPixel(x, y, px[x, y, 0], px[x, y, 1], px[x, y, 2])
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)

    def start(self, brightness=None):
        self.options["power"] = True
        self.rgb_thread = threading.Thread(target=self._start_rgb, name="RGB Matrix", args=(brightness,))
        self.rgb_thread.start()

    def stop(self):
        self.options["power"] = False
        self.alive = False
        if self.rgb_thread is not None:
            print("attempting to turn off matrix")
            self.rgb_thread.join()

    def set_brightness(self, brightness):
        self.options = brightness
        self.stop()
        self.start(brightness)


rgb = RGBHandler()


@app.route('/')
def main_page():
    power = "on" if rgb.options["power"] else "off"
    brightness = rgb.options["brightness"]
    token = dcfg["token"]
    name = sp.me()["display_name"] if sp is not None else ""
    img = sp.me()["images"][0]["url"] if sp is not None else ""
    return render_template("index.html", power=power, brightness=brightness, token=token, name=name, img=img)


@app.route('/login', methods=["POST"])
def handle_login():
    getparams = urlencode(dict(
        response_type="code",
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        scope=scope,
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"))
    )
    url = f"https://accounts.spotify.com/authorize?{getparams}"
    # print("Redirecting to", url)
    return redirect(url)


@app.route('/logincallback', methods=["GET", "POST"])
def handle_login_callback():
    code = request.args.get("code")
    auth = spotipy.SpotifyOAuth()
    token = auth.get_access_token(code=code, as_dict=False)
    write_cfg("token", token)
    global sp
    sp = spotipy.Spotify(auth=token)
    test_sp_connection()
    return redirect("/")


@app.route('/power', methods=["POST"])
def handle_power():
    power = request.form["power"]
    if power == "on":
        rgb.start()
        print("RGB thread: ", rgb.rgb_thread)
    else:
        rgb.stop()
    return redirect('/')


@app.route('/brightness', methods=["POST"])
def handle_brightness():
    brightness = request.form["brightness"]
    write_cfg("brightness", brightness)
    # restart RGB with given brightness
    return redirect('/')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
