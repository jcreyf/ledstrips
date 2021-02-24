#!/usr/bin/env python3
#***********************************************************************************************************#
# Bare basic app to drive a 7 meter LED strip with a standard electrical light switches just like any       #
# ordinary light bulb in the house. All leds on the strip just lighting up bright white or off.             #
#                                                                                                           #
# Led strips data line connected to pin 12 on the RPi (GPIO 18)                                             #
# Light switch 1 connected to pin 16 (GPIO 23) and pin 1 (3v3) to give it power through a 12kOhm resistor   #
# Light switch 2 connected to pin 18 (GPIO 24) and pin 17 (3v3) to give it power through a 12kOhm resistor  #
#***********************************************************************************************************#
from jcreyf_ledstrip import Light, Switch
from time import sleep
import yaml
import sys

DEBUG=False

def debug(*args):
  """ Simple function to print messages to the console if the DEBUG-flag is set. """
  if DEBUG:
    print(("debug -> {}").format(args))


#--------------------------------------------------#
# The app starts here...
#--------------------------------------------------#
if __name__ == '__main__':
  print("Reading the config...")
  lights=[]    # list of Light objects (typically 1)

  with open("lights.yaml", 'r') as stream:
    try:
      config=yaml.safe_load(stream)
    except yaml.YAMLError as exc:
      print(exc)
      sys.exit(1)

  # There may be config for multiple lights in the yaml-file.
  # Lets set them all up:
  debug("config:", config)
  debug("Number of light configurations:", len(config))
  for light_config in config:
    print("Light:")
    debug("light config:", light_config)
    light_config=light_config["light"]
    debug("light:", light_config)
    _name=light_config['name']
    _ledCount=light_config['led_count']
    _brightness=light_config['brightness']
    _gpioPin=light_config['gpio_pin']
    print(" name:", _name)
    print(" led count:", _ledCount)
    print(" brightness:", _brightness)
    print(" GPIO pin:", _gpioPin)
    # Create a light instance and set its properties:
    light=Light(_name)
    light.ledCount=_ledCount
    light.ledBrightness=_brightness
    light.stripGpioPin=_gpioPin
    light.Start()
    # Each light may have 0 or more switches to control it.
    # Lets set them all up for this light:
    switches_config=light_config['switches']
    for switch_config in switches_config:
      print(" switch:")
      switch_config=switch_config['switch']
      debug("switch:", switch_config)
      _name=switch_config['name']
      _gpioPin=switch_config['gpio_pin']
      print("  name:", _name)
      print("  GPIO pin:", _gpioPin)
      # Create the switch and set its properties:
      switch=Switch(_name)
      switch.gpioPin=_gpioPin
      switch.init()
      light.addSwitch(switch)
    # Add the light to the list and move on to the next one (if any)
    lights.append(light)

  # List the Lights and their Switch objects (if any):
  for light in lights:
    debug(("Light object: {}").format(light.name)
    for switch in light.switches:
      debug(("  Switch object: {}").format(switch.name)

  print('Press Ctrl-C to quit.')

  try:
    while True:
      # Infinite loop, checking each button status every so many milliseconds and toggling the lights
      # if a change in one of the switches is detected:
      sleep(0.5)
      for light in lights:
        for switch in light.switches:
          if switch.hasChanged():
            light.Toggle()

  except KeyboardInterrupt:
    # Ctrl-C was hit!
    # Destroy the objects, invoking their destructors, which will turn off the light and clean up all the resources.
    # Then stop the app...
    for light in lights:
      for switch in light.switches:
        del switch
      del light

  finally:
    # Release the ports that were setup on the RPi for this app:
    Switch.cleanUp()
    print("I'm out of here! Adios...\n")