#!/usr/bin/env python3
#***********************************************************************************************************#
# Bare basic app to drive a 7 meter LED strip with a standard electrical light switches just like any       #
# ordinary light bulb in the house.  All leds on the strip just lighting up bright white or off.            #
#                                                                                                           #
# Led strips data line connected to pin 12 on the RPi (GPIO 18)                                             #
# Light switch 1 connected to pin 16 (GPIO 23) and pin 1 (3v3) to give it power through a 12kOhm resistor   #
# Light switch 2 connected to pin 18 (GPIO 24) and pin 17 (3v3) to give it power through a 12kOhm resistor  #
#***********************************************************************************************************#
from time import sleep
from RPi import GPIO
from rpi_ws281x import Color, PixelStrip, ws

# LED strip configuration:
LED_COUNT = 215       # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0
LED_STRIP = ws.SK6812_STRIP_RGBW

# Light on or off:
LIGHT_STATUS = False

# Light switch 1 connected to pin 16 (GPIO 23) and pin 1 (3v3) to give it power through a 12kOhm resistor:
SWITCH_1_GPIO = 23
SWITCH_1_STATUS = False

# Light switch 2 connected to pin 18 (GPIO 24) and pin 17 (3v3) to give it power through a 12kOhm resistor:
SWITCH_2_GPIO = 24
SWITCH_2_STATUS = False


def lightsOn(strip):
  """Turn on the leds"""
  print("turn on lights")
  # Set the leds to white, full brightness:
  color = Color(0, 0, 0, 255)
  for i in range(strip.numPixels()):
    strip.setPixelColor(i, color)
  strip.show()

def lightsOff(strip):
  """Turn off the leds"""
  print("turn off lights")
  color = Color(0, 0, 0, 0)
  for i in range(strip.numPixels()):
    strip.setPixelColor(i, color)
  strip.show()

def toggleLight(strip):
  """Change the status of the light"""
  global LIGHT_STATUS
  _flag = LIGHT_STATUS
  _switch1 = GPIO.input(SWITCH_1_GPIO)
  if SWITCH_1_STATUS != _switch1:
    _flag = not _flag

  _switch2 = GPIO.input(SWITCH_2_GPIO)
  if SWITCH_2_STATUS != _switch2:
    _flag = not _flag

  if LIGHT_STATUS != _flag:
    if _flag:
      lightsOn(strip)
    else:
      lightsOff(strip)
    LIGHT_STATUS = _flag


# Main program:
if __name__ == '__main__':
  # Create PixelStrip object with appropriate configuration.
  global strip
  strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
  # Intialize the library (must be called once before other functions).
  strip.begin()

  GPIO.setmode(GPIO.BCM)
  # Create button objects for both switches:
  GPIO.setup(SWITCH_1_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(SWITCH_2_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

  # Read the current status of the switches and set the light accordingly:
  toggleLight(strip)

  print('Press Ctrl-C to quit.')

  try:
    while True:
      # Infinite loop, checking the button status every so many milliseconds
      toggleLight(strip)
      sleep(0.5)

  except KeyboardInterrupt:
    # Ctrl-C was hit.  Stop the app!
    lightsOff(strip)
    GPIO.cleanup()
