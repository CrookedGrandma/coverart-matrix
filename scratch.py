def _start_rgb(self, brightness):
    print("Brightness at thread:", brightness)
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 32
    if brightness is None:
        options.brightness = self.options["brightness"]
    else:
        options.brightness = brightness
        self.options["brightness"] = brightness
    self.matrix = RGBMatrix(options=options)
    offset_canvas = self.matrix.CreateFrameCanvas()
    t = threading.current_thread()
    t.alive = True
    while t.alive:
        px = self.get_img()
        for x in range(0, self.matrix.width):
            for y in range(0, self.matrix.height):
                offset_canvas.SetPixel(x, y, px[x, y, 0], px[x, y, 1], px[x, y, 2])
        offset_canvas = self.matrix.SwapOnVSync(offset_canvas)
        time.sleep(5)

    self.matrix.SwapOnVSync(self.matrix.CreateFrameCanvas())

def get_img(self):
    track = self.sp.current_user_playing_track()
    if track is None:
        url = "black"
    else:
        url = track["item"]["album"]["images"][0]["url"]
    if url == self.currentimg:
        return self.currentpx
    else:
        self.currentimg = url
        if url == "black":
            img = Image.open("black.png")
        else:
            try:
                img = Image.open(BytesIO(requests.get(url).content))
            except requests.RequestException as e:
                img = Image.open("black.png")
                print(e)
        img.thumbnail((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
        img = img.convert("RGB")
        px = np.array(img)
        self.currentpx = px
        return px