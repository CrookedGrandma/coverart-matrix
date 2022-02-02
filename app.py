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


def test_sp_connection(sp):
    try:
        sp.me()
    except spotipy.exceptions.SpotifyException:
        cfg.set(d, "token", "")
        with open(cfgfile, "w") as configfile:
            cfg.write(configfile)


scope = "user-read-currently-playing"
sp = None
if dcfg["token"] != "":
    sp = spotipy.Spotify(auth=dcfg["token"])
    test_sp_connection(sp)


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
    return render_template("index.html", power=power, brightness=brightness, token=token)


@app.route('/login', methods=["POST"])
def handle_login():
    getparams = urlencode(dict(
        response_type="code",
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        scope=scope,
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"))
    )
    return redirect(f"https://accounts.spotify.com/authorize?{getparams}")


@app.route('/logincallback')
def handle_login_done():
    code = request.args.get("code")
    # POST request to 'https://accounts.spotify.com/api/token'
    global sp
    sp = spotipy.Spotify(auth=code)
    test_sp_connection(sp)
    return redirect("/")


@app.route('/power', methods=["POST"])
def handle_power():
    power = request.form["power"]
    brightness = int(dcfg["brightness"])
    cfg.set(d, "power", power)
    with open(cfgfile, "w") as configfile:
        cfg.write(configfile)
    if power == "on":
        start_rgb(brightness)
    else:
        stop_rgb()
    return redirect('/')


if __name__ == "__main__":
    app.run(port=80)
