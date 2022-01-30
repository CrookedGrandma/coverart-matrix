import time
import sys, os

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image

if len(sys.argv) < 2:
    image_file = "testimg.png"
else:
    image_file = sys.argv[1]

image_file = os.path.join(os.path.dirname(__file__), image_file)
image = Image.open(image_file)

options = RGBMatrixOptions()
options.rows = 32
options.cols = 32
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = "regular"

matrix = RGBMatrix(options=options)

image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)

matrix.SetImage(image.convert('RGB'))

try:
    print("Press CTRL-C to stop.")
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    sys.exit(0)
