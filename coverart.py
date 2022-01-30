from samplebase import SampleBase
from random import randint
import math

class TestBoy(SampleBase):
    def __init__(self, *args, **kwargs):
        super(TestBoy, self).__init__(*args, **kwargs)
    
    def col(self, val, mult):
        w = self.matrix.width
        f = val / w
        f2pi = 2 * math.pi * f
        return math.floor((math.sin(mult * f2pi) + 1) / 2 * 255)
    
    def run(self):
        offset_canvas = self.matrix.CreateFrameCanvas()
        while True:
            for x in range(0, self.matrix.width):
                for y in range(0, self.matrix.height):
                    offset_canvas.SetPixel(x, y, self.col(x+y, 1), self.col(x+y, 1.4), self.col(x+y, 1.8))
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)


if __name__ == "__main__":
    testboy = TestBoy()
    if (not testboy.process()):
        testboy.print_help()
