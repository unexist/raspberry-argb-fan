#
# @file raspberry-argb-fan
#
# @copyright (c) 2026-present, Christoph Kappel <christoph@unexist.dev>
# @version $Id$
#
# This program can be distributed under the terms of the GNU GPL.
# See the file COPYING
#

from flask import Flask, render_template, request, jsonify
import time
import board
import neopixel
from threading import Timer

app = Flask(__name__)

PIXEL_PIN = board.D21
NUM_PIXELS = 12
MAX_BRIGHTNESS=0.5
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=MAX_BRIGHTNESS, auto_write=False, pixel_order=ORDER)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)

    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

def rainbow_cycle():
    for j in range(255):
        for i in range(NUM_PIXELS):
            pixel_index = (i * 256 // NUM_PIXELS) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(0.2)

rainbow_timer = Timer(2.0, rainbow_cycle)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/colors', methods=['POST'])
def colors():
    data = request.json
    color = data.get('colordata')

    color = color.lstrip('#')
    color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

    pixels.fill(color)
    pixels.show()

    return jsonify({"message": "Color received"})

@app.route('/rainbow', methods=['POST'])
def rainbow():
    global rainbow_timer

    if rainbow_timer.is_alive():
        rainbow_timer.cancel()
    else:
        rainbow_timer.start()

    return jsonify({"message": "Rainbow started"})

if __name__ == '__main__':
    pixels.fill((255, 0, 0))
    pixels.show()

    app.run(host='0.0.0.0', port = 80, debug=False)
