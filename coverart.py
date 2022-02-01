from PIL import Image
from samplebase import SampleBase
import numpy as np
import sys


class TestBoy(SampleBase):
    def __init__(self, *args, **kwargs):
        super(TestBoy, self).__init__(*args, **kwargs)
        self.parser.add_argument("-i", "--img", help="The image to show", default="./testimg2.png")

    def run(self):
        img = Image.open(self.args.img)
        img.thumbnail((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
        img = img.convert("RGB")
        px = np.array(img)
        offset_canvas = self.matrix.CreateFrameCanvas()
        while True:
            for x in range(0, self.matrix.width):
                for y in range(0, self.matrix.height):
                    offset_canvas.SetPixel(x, y, px[x, y, 0], px[x, y, 1], px[x, y, 2])
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)


if __name__ == "__main__":
    testboy = TestBoy()
    if not testboy.process():
        testboy.print_help()
