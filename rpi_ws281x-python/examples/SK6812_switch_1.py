#!/usr/bin/env python 

from time import sleep
from RPi import GPIO
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

# Main program:
if __name__ == '__main__':
  print("GPIO non-event based (all processing in same thread)...")

  # Create PixelStrip object with appropriate configuration.
  global strip
  strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
  # Intialize the library (must be called once before other functions).
  strip.begin()
  # Create a Button object on GPIO port 24 (physical pin 18 on the RPi board ... use "GPIO.setmode(GPIO.BOARD)" if you set this value to 18)
  switchPin = 24
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(switchPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  # Read the current status of the switch and set the light accordingly:
  toggleStatus(strip, GPIO.input(switchPin))

  print('Press Ctrl-C to quit.')

  try:
    while True:
      # Infinite loop, checking the button status every so many milliseconds
      toggleStatus(strip, GPIO.input(switchPin))
      sleep(0.5)

  except KeyboardInterrupt:
    # Ctrl-C was hit.  Stop the app
    lightsOff(strip)
    GPIO.cleanup()
