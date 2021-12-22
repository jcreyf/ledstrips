"""
This module contains the classes for both the 'Light' and 'Switch' objects:
- a 'Light' object is a LED strip with 1 or more individually addressable LEDs and may have 0 or more Switch
  objects linked to it for control;
- a 'Switch' object is a GPIO pin on the Raspberry PI that gets pulled up or down to either turn on or
  turn off the LEDs on the strip;

This module requires these modules:
- Raspberry PI GPIO class from the RPi module;
- Color, ws and PixelStrip classes from the rpi_ws281x module; 
"""

import BehaviorModules
from RPi import GPIO
#from rpi_ws281x import Color, PixelStrip, ws
from rpi_ws281x import ws
from time import sleep
#import threading


class Light:
  """
  Class that represents a LED light strip connected to a Raspberry PI through a single I/O port.
  Data going through that I/O port and power supplied externally (because it's too much for the PI
  to power them if there are too many).
  """

  def __init__(self, name: str):
    """ Constructor, initializing members with default values. """
    print(f"  ..creating light object: {name}")
    self._name=name                        # Human name of the LED strip;
    self._switches=[]                      # Optional list of Switch objects that are linked to this light object;
    self._debug=False                      # Debug level logging;
    self._behaviorModuleName="Default"     # Name of the module that has the code to turn the leds on/off
    self._behaviorModule=BehaviorModules.BehaviorModule()              # The actual BehaviorModule object
    self._ledSettings={
      "ledCount": 100,                     # Number of individually addressable LEDs on the strip;
      "redRGB": 1,                         # RGB Red color value;
      "greenRGB": 1,                       # RGB Green color value;
      "blueRGB": 1,                        # RGB Blue color value;
      "ledBrightness": 255,                # Set to 0 for darkest and 255 for brightest;
      "ledFrequency": 800000,              # LED signal frequency in hertz (usually 800khz);
      "ledDmaChannel": 10,                 # DMA channel to use for generating signal (try 10);
      "ledInvert": False,                  # True to invert the signal (when using NPN transistor level shift);
      "ledChannel": 0,
      "stripGpioPin": 18,                  # RaspberryPI GPIO pin that is used to drive the LED strip;
      "stripType": ws.SK6812_STRIP_RGBW,   # The type of the LED strip (just RGB or does it also include a White LED);
      "strip": None,                       # Instance of the rpi_ws281x LED strip;
      "lightState": False                  # Is the light "off" (false) or "on" (true);
    }

  def __del__(self):
    """ Destructor will turn off this light. """
    print(f"destroying light object: {self._name}")
    self.Off()

  @property
  def name(self):
    """ Return the name of this light. """
    return self._name
  
  @name.setter
  def name(self, value: str):
    """ Set the name for this light. """
    self._name=value

  @property
  def ledCount(self) -> int:
    """ Return the number of individual LEDs on the light strip. """
    return self._ledSettings["ledCount"]
  
  @ledCount.setter
  def ledCount(self, value: int):
    """ Set the number of LEDs to use on this light strip.  You can activate fewer than available. """
    if not (value > 0): raise Exception("You need to have at least 1 LED on the strip!")
    self._ledSettings["ledCount"]=value

  @property
  def redRGB(self) -> int:
    """ Return the current Red RGB color value for the light strip. """
    return self._ledSettings["redRGB"]
  
  @redRGB.setter
  def redRGB(self, value: int):
    """ Set the red RGB color value of LEDs to use on this light strip. """
    if not ((value >= 0) and (value <= 255)): raise Exception("The red RGB value needs to be between 0 and 255!")
    self._ledSettings["redRGB"]=value

  @property
  def greenRGB(self) -> int:
    """ Return the current Green RGB color value for the light strip. """
    return self._ledSettings["greenRGB"]
  
  @greenRGB.setter
  def greenRGB(self, value: int):
    """ Set the green RGB color value of LEDs to use on this light strip. """
    if not ((value >= 0) and (value <= 255)): raise Exception("The green RGB value needs to be between 0 and 255!")
    self._ledSettings["greenRGB"]=value

  @property
  def blueRGB(self) -> int:
    """ Return the current Blue RGB color value for the light strip. """
    return self._ledSettings["blueRGB"]
  
  @blueRGB.setter
  def blueRGB(self, value: int):
    """ Set the blue RGB color value of LEDs to use on this light strip. """
    if not ((value >= 0) and (value <= 255)): raise Exception("The blue RGB value needs to be between 0 and 255!")
    self._ledSettings["blueRGB"]=value

  @property
  def ledBrightness(self) -> int:
    """ Return the brightness that the LED have been configured with (0 to 255). """
    return self._ledSettings["ledBrightness"]
  
  @ledBrightness.setter
  def ledBrightness(self, value: int):
    """ Set the brightness of the LEDs (0 to 255). """
    if not ((value > 0) and (value <= 255)): raise Exception("Brightness needs to be between 1 and 255!")
    self._ledSettings["ledBrightness"]=value

  @property
  def stripGpioPin(self) -> int:
    """ Return the Raspberry PI GPIO pin the LED strip is connected to (data). """
    return self._ledSettings["stripGpioPin"]

  @stripGpioPin.setter
  def stripGpioPin(self, value: int):
    """ Set the Raspberry PI GPIO pin the LED strip is connected to (data). """
    # The number of valid GPIO ports is limited and specific.
    # A good validator should check the port based on RPi model and throw an exception if the
    # selected port does not work to drive a LED strip like these.
    # I've decided to have a very rough validator here that enforces a port between 2 and 26.
    # I know this is not a great validator and I should probably make it more specific at some point.
    if not ((value >= 2) and (value <= 26)): raise Exception("The RPi GPIO port needs to be between 2 and 26!")
    self._ledSettings["stripGpioPin"]=value

  @property
  def state(self) -> bool:
    """ Show if the light is currently on or off.  "True" means "On" and "False" means "Off". """
    return self._ledSettings["lightState"]

  @property
  def debug(self) -> bool:
    """ Return the debug-flag that is set for this light. """
    return self._debug

  @debug.setter
  def debug(self, flag: bool):
    """ Set the debug level. """
    self._debug=flag

  @property
  def behaviorModuleName(self):
    """ Return the name of the behavior module to run. """
    return self._behaviorModuleName
  
  @name.setter
  def behaviorModuleName(self, value: str):
    """ Set the name for the behavior module to run. """
    # Do not change anything if the same behavior is selected.
    if self._behaviorModuleName != value:
      # The behavior is changing.  Call the finalizer of the current behavior to get resources released:
      self._behaviorModule.Finalize()
      self._behaviorModule=None
      # Now set the new behavior:
      if value == "Christmass":
        self._behaviorModule=BehaviorModules.ChristmassModule(self._ledSettings)
      else:
        # Set the default On/Off behavior:
        self._behaviorModule=BehaviorModules.DefaultModule(self._ledSettings)
      self._behaviorModuleName=self._behaviorModule.name

  @property
  def switches(self) -> list:
    """ Return a list of 0 or more Switch objects that have been mapped to this light. """
    return self._switches

  def addSwitch(self, switch):
    """ Add a new Switch object that can control this light. """
    self._switches.append(switch)

  def delSwitch(self, switch):
    """ Remove a switch from this light. """
    self._switches.remove(switch)
    del switch

  def On(self):
    """ Turn the leds on. """
    self._behaviorModule.On()

  def Off(self):
    """ Turn the leds off. """
    self._behaviorModule.Off()
  
  def Toggle(self):
    """ Toggle the light on or off. """
    if self.state:
      self.Off()
    else:
      self.On()

  def Update(self):
    """ Apply the Updated LED settings if they are on. """
    if self.state:
      self.Off()
      self.On()


#
#----------------------------------
#
class Switch:
  """
  Class that represents a typical and standard on/off toggle switch connected to a Raspberry PI.

  A 'Switch' is basically a GPIO pin on the Raspberry PI that gets pulled high for the 'On' position
  and low for the 'Off' position.
  """

  def __init__(self, name: str):
    """ Constructor setting some default values. """
    print(f"  ..creating switch object: {name}")
    self._state=True
    self._name=name
    self._gpioPin=0

  def __del__(self):
    """ Destructor to release and clean up GPIO resources. """
    print(f"destroying switch object: {self._name}")

  @property
  def state(self) -> bool:
    """ Return the actual current state of the switch from the Raspberry PI GPIO port. """
    self._state=GPIO.input(self._gpioPin)
    return self._state

  @property
  def name(self) -> str:
    """ Return the name that was set for this switch. """
    return self._name

  @name.setter
  def name(self, value: str):
    """ Set a name for this switch. """
    self._name=value

  @property
  def gpioPin(self) -> int:
    """ Return the Raspberry PI GPIO pin that is use to connect this switch to. """
    return self._gpioPin

  @gpioPin.setter
  def gpioPin(self, value: int):
    """ Set the Raspberry PI GPIO pin that is use to connect this switch to. """
    # The number of valid GPIO ports is limited and specific.
    # A good validator should check the port based on RPi model and throw an exception if the
    # selected port does not work to drive a LED strip like these.
    # I've decided to have a very rough validator here that enforces a port between 2 and 26.
    # I know this is not a great validator and I should probably make it more specific at some point.
    if not ((value >= 2) and (value <= 26)): raise Exception("The RPi GPIO port needs to be between 2 and 26!")
    self._gpioPin=value

  def hasChanged(self) -> bool:
    """ Method to detect if the state of the switch has changed since last time we checked. """
    oldState=self._state
    ret=False
    if oldState != self.state:
      # Turns out we sometimes get false positives for some reason.
      # It looks like voltage sometimes drops below the threshold value on longer wires from the
      # RPi to the physical switch, triggering a false positive.  The RPi thinks the switch got triggered
      # and then switches the light on or off.  It sees the correct state again during the next loop
      # half a second later and then turns the light on or off again.
      # The best fix would be to use better quality wires and better pull up resitors but the cheapest
      # and easiest solution is to have the RPi check the status again after a short time and only decide
      # if both checks come back with the same result.
      sleep(0.1)
      if oldState != self.state:
        ret=True
    return ret

  def init(self):
    """ Method to initialize the Raspberry PI hardware at GPIO level. """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self._gpioPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

  def cleanUp():
    """ Static method to cleanup the GPIO ports that this app used on the RPi. """
    GPIO.cleanup()
