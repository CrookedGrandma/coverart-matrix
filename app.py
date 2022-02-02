import os
import requests
import spotipy
import time
import threading
from configparser import ConfigParser
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect
from urllib.parse import urlencode

load_dotenv()
app = Flask(__name__)

cfgfile = "config.ini"
cfg = ConfigParser()
cfg.read(cfgfile)
d = "DEFAULT"
dcfg = cfg[d]

rgb_thread = None


def write_cfg(name, val):
    cfg.set(d, name, val)
    with open(cfgfile, "w") as configfile:
        cfg.write(configfile)


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


def _start_rgb(brightness):
    t = threading.current_thread()
    t.alive = True
    while t.alive:
        print("alive at", time.strftime("%H:%M:%S", time.localtime()))
        time.sleep(1)


def start_rgb(brightness=100):
    global rgb_thread
    rgb_thread = threading.Thread(target=_start_rgb, name="RGB Matrix", args=(brightness,))
    rgb_thread.start()


def stop_rgb():
    global rgb_thread
    if rgb_thread is not None:
        rgb_thread.alive = False
        print("thread.alive set to False")
        rgb_thread.join()


@app.route('/')
def main_page():
    power = dcfg["power"]
    brightness = int(dcfg["brightness"])
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
    brightness = int(dcfg["brightness"])
    write_cfg("power", power)
    if power == "on":
        start_rgb(brightness)
    else:
        stop_rgb()
    return redirect('/')


if __name__ == "__main__":
    app.run(port=80)
