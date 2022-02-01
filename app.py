import os
import sys
import time
from configparser import ConfigParser
from flask import Flask, render_template, request, redirect
from stoppablethread import StoppableThread

app = Flask(__name__)

cfgfile = "config.ini"
cfg = ConfigParser()
cfg.read(cfgfile)
d = "DEFAULT"
dcfg = cfg[d]

rgb_thread = None


def _start_rgb(brightness):
    print("test")
    time.sleep(10)
    print(f"test later, brightness = {brightness}")


def start_rgb(brightness=100):
    global rgb_thread
    rgb_thread = StoppableThread(target=_start_rgb, name="RGB Matrix", args=(brightness,))
    rgb_thread.start()


def stop_rgb():
    global rgb_thread
    if rgb_thread is not None:
        rgb_thread.stop()


@app.route('/')
def main_page():
    power = dcfg["power"]
    brightness = int(dcfg["brightness"])
    return render_template("index.html", power=power, brightness=brightness)


@app.route('/power', methods=["GET", "POST"])
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
