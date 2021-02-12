#!/usr/bin/env python 

from time import sleep
from gpiozero import Button   # https://gpiozero.readthedocs.io/en/stable/
from rpi_ws281x import Color, PixelStrip, ws

# LED strip configuration:
LED_COUNT = 215       # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0
# LED_STRIP = ws.SK6812_STRIP_RGBW
LED_STRIP = ws.SK6812W_STRIP

STATUS = False

# Function to turn on the lights
def lightsOn(strip):
  """Turn on the lights"""
  print("turn on lights")
  color = Color(0, 0, 0, 255)  # White LEDs full brightness
  for i in range(strip.numPixels()):
    strip.setPixelColor(i, color)
  strip.show()

# Function to turn on the lights
def lightsOff(strip):
  """Turn off the lights"""
  print("turn off lights")
  color = Color(0, 0, 0, 0)
  for i in range(strip.numPixels()):
    strip.setPixelColor(i, color)
  strip.show()

# Function to detect a status change and turn the lights on or off accordingly
def toggleStatus(strip, flag):
  """Change the STATUS of the light"""
  global STATUS
  if STATUS != flag:
    if flag:
      lightsOn(strip)
    else:
      lightsOff(strip)
    STATUS = flag

# This eventhandler ends up running in a separate thread and is not responding fast enough!!!
def switchEvent():
  global strip
  toggleStatus(strip, switch.value)


# Main program:
if __name__ == '__main__':
  print("gpizero Button event based (switch toggle processing in different thread)...")

  # Create PixelStrip object with appropriate configuration.
  global strip
  strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
  # Intialize the library (must be called once before other functions).
  strip.begin()
  # Create a Button object on GPIO port 24 (physical pin 18 on the RPi board)
  switchPin = 24
  switch = Button(switchPin, False)
  # Read the current status of the switch and set the light accordingly:
  toggleStatus(strip, switch.value)

  # Add event handler on the switch to detect it getting flipped by a user:
  switch.when_pressed = switchEvent
  switch.when_released = switchEvent

  print('Press Ctrl-C to quit.')

  try:
    while True:
      # Infinite loop, doing nothing but pass time...
      pass

  except KeyboardInterrupt:
    # Ctrl-C was hit.  Stop the app
    lightsOff(strip)
