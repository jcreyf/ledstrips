import time
from random import randrange
from rpi_ws281x import Color, PixelStrip, ws

# LED strip configuration:
LED_COUNT = 150       # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0
# LED_STRIP = ws.SK6812_STRIP_RGBW
LED_STRIP = ws.SK6812W_STRIP

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    time.sleep(wait_ms / 1000.0)


# Main program logic follows:
if __name__ == '__main__':
    # Create PixelStrip object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')
    wait_ms = 1000

    try:

      while True:
        bright = randrange(0, 255, 1)
        pos = randrange(1, LED_COUNT, 1)
        r = randrange(0, 255, 1)
        g = randrange(0, 255, 1)
        b = randrange(0, 255, 1)
        strip.setPixelColor(pos, Color(r, g, b, 0))
        strip.show()

    except KeyboardInterrupt:
        colorWipe(strip, Color(0, 0, 0), 0)
