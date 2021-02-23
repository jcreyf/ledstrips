"""
This is a mock file to get the app running on a host that doesn't have the
Raspberry PI ws281x libraries and modules installed.
"""
class Color:
  def __init__(self, v1, v2, v3, v4):
    pass


class PixelStrip:
  def __init__(self, v1, v2, v3, v4, v5, v6, v7, v8):
    pass

  def begin(self):
    pass

  def numPixels(self):
    return 1

  def setPixelColor(self, v1, v2):
    pass

  def show(self):
    pass


class ws:
  SK6812_STRIP_RGBW = None