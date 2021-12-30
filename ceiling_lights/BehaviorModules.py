"""
This module contains the classes for both the multiple light behavior modules.
A Behavior Module contains specific code to manipulate the leds on the ledstrip.
The DefaultModule will simply turn on/off all leds at the same time on the strip,
whereas other modules can create more visual effects (like the ChristmassModule doing more
colorfull things).

This module requires these modules:
- Color, ws and PixelStrip classes from the rpi_ws281x module;
- Threading to allow visual effects to happen in their own non-blocking thread;
"""

import threading
import sys
from rpi_ws281x import Color, PixelStrip, ws
from time import sleep


#
#----------------------------------
#
class BehaviorModule():
  """
  Template Class for ledstrip behavior modules.
  """
  def __init__(self, name: str="Blank", ledSettings: dict=None):
    """ Constructor of our BehaviorModule instance.
    
    Arguments:
      name (str):         the name of this specific behavior (default="Blank").
                          (others could be: "Default", "Christmass", ...)
      ledSettings (dict): dictionary with settings that we need to drive the ledstrip.
                          required_settings={
                            "ledCount": <1..N>,           # Number of individually addressable LEDs on the strip;
                            "redRGB": <0..255>,           # RGB Red color value;
                            "greenRGB": <0..255>,         # RGB Green color value;
                            "blueRGB": <0..255>,          # RGB Blue color value;
                            "whiteRGB": <0..255>,         # Value for the white led;
                            "ledBrightness": <0..255>,    # Set to 0 for darkest and 255 for brightest;
                            "ledFrequency": 800000,       # LED signal frequency in hertz (usually 800khz);
                            "ledDmaChannel": 10,          # DMA channel to use for generating signal (try 10);
                            "ledInvert": False,           # True to invert the signal (when using NPN transistor level shift);
                            "ledChannel": 0,
                            "stripGpioPin": 18,           # RaspberryPI GPIO pin that is used to drive the LED strip;
                            "strip": None,                # Instance of the rpi_ws281x LED strip;
                            "lightState": [True|False]    # Is the light "off" (false) or "on" (true);
                          }
    """
    self._name=name
    self._debug=True
    self._ledSettings=ledSettings
    # The type of the LED strip (just RGB or does it also include a White LED);
    self._stripType=ws.SK6812_STRIP_RGBW
    self.log("Constructor")
    self.log(f"ledSettings: {ledSettings}", debug=True)

  def __del__(self):
    """ Destructor will turn off the leds and release resources. """
    self.log("Destructor")
# We want all our behaviors to use the rpi_ws281x.PixelStrip wrapper.
# The rpi_ws281x.PixelStrip class has an 'atexit' method registered to automatically release and clean up its resources
# when the app exits.
# We can explicitly clean up by setting the object to None and/or call the finalize method.
# Because of that, there's no need to destroy the resources and recreate new ones each time we switch between behaviors!
#    self._ledSettings["strip"]=None

  def finalize(self):
    """ Method to release and cleanup resources. """
    # Release the ledstrip properly if we have one set:
    if isinstance(self._ledSettings["strip"], PixelStrip):
      self._ledSettings["strip"]._cleanup()
      self._ledSettings["strip"]=None

  @property
  def name(self) -> str:
    """ Return the name of this behavior module. """
    return self._name

  @property
  def debug(self) -> bool:
    """ Return the debug-flag that is set for this light. """
    return self._debug

  @debug.setter
  def debug(self, flag: bool):
    """ Set the debug level. """
    self._debug=flag

  def log(self, *args, debug: bool=False):
    """ Simple function to log messages to the console. """
    _log=True
    if debug and not self._debug:
      _log=False
    if _log:
      # We don't want to log the message as a list between '()' if we only got 1 element in the argument list:
      if len(args) == 1:
        print(f"{type(self)}: {args[0]}")
      else:
        print(f"{type(self)}: {args}")
      # We need to flush the stdout buffer in python for log statements to reach the Linux systemd journal:
      sys.stdout.flush()

  def On(self):
    """ Method to start the behavior. """
    self.log("On()")
    self.log(f"ledSettings: {self._ledSettings}", debug=True)

  def Off(self):
    """ Method to stop the behavior. """
    self.log("Off()")
    self.log(f"ledSettings: {self._ledSettings}", debug=True)


#
#----------------------------------
#
class DefaultModule(BehaviorModule):
  """
  Behavior Module to implement basic On/Off functionality.
  """
  def __init__(self, ledSettings: dict):
    """ Constructor """
    super().__init__(name="Default", ledSettings=ledSettings)
    self.log(f"ledSettings: {ledSettings}", debug=True)

  def __del__(self):
    """ Destructor will turn off the leds and release resources. """
    self.log("Finalizing and cleaning up resources...", debug=True)
# We want all our behaviors to use the rpi_ws281x.PixelStrip wrapper.
# Because of that, there's no need to destroy the resources and recreate new ones each time we switch between behaviors!
#    self._ledSettings["strip"]=None

  def run(self):
    """ We don't need any code running in a separate thread for this basic On/Off behavior. """
    self.log("Thread started but no code to run", debug=True)

  def On(self):
    """ Turn the behavior on, which is basically simply turning the light on. """
    self.log("On()")
    self.Code(state=True)

  def Off(self):
    """ Turn the behavior on, which is basically simply turning the light off. """
    self.log("Off()")
    self.Code(state=False)

  def Code(self, state: bool):
    """ Here we have the actual code to turn the ledstrip on or off.

    Arguments:
      state (bool): True == turn leds on; False == turn leds off
    """
    self.log(f"ledSettings -> {self._ledSettings}", debug=True)
    # Initialize the ledstrip if that's not done yet:
    if self._ledSettings["strip"] == None:
      # PixelStrip.__init__(self, num, pin, freq_hz=800000, dma=10, invert=False, brightness=255, \
      #                           channel=0, strip_type=None, gamma=None):
      self._ledSettings["strip"]=PixelStrip(num=self._ledSettings["ledCount"], \
                  pin=self._ledSettings["stripGpioPin"], \
                  freq_hz=self._ledSettings["ledFrequency"], \
                  dma=self._ledSettings["ledDmaChannel"], \
                  invert=self._ledSettings["ledInvert"], \
                  brightness=self._ledSettings["ledBrightness"], \
                  channel=self._ledSettings["ledChannel"], \
                  strip_type=self._stripType)
      # Initialize the library (must be called once before other functions):
      self._ledSettings["strip"].begin()
    if state:
      # Turn the leds on.
      # Generate the color setting for each led:
# ToDo: Color(red, green, blue, white=0) -> so 'ledBrightness' is in fact just the intensity of the separate white led on the SK6812 strip!
      color=Color(green=self._ledSettings["greenRGB"], \
                  red=self._ledSettings["redRGB"], \
                  blue=self._ledSettings["blueRGB"], \
                  white=self._ledSettings["ledBrightness"])
      self.log("turn leds on", debug=True)
    else:
      # Turn the leds off.
      # The color setting of each led needs to be set to 0:
      color=Color(0, 0, 0, 0)
      self.log("turn leds off", debug=True)
    # Loop and apply the color setting to all leds on the strip:
    for i in range(self._ledSettings["strip"].numPixels()):
      self._ledSettings["strip"].setPixelColor(i, color)
    # Update the brightness of the leds:
    self._ledSettings["strip"].setBrightness(self._ledSettings["ledBrightness"])
    # Force the ledstrip to show the applied changes:
    self._ledSettings["strip"].show()
    # Set our light status accordingly:
    self._ledSettings["lightState"]=state



#
#----------------------------------
#
class ChristmassModule(BehaviorModule):
  """
  Behavior Module to implement Christmass light effect functionality.
  """
  def __init__(self, ledSettings: dict):
    """ Constructor """
    super().__init__(name="Christmass", ledSettings=ledSettings)
    self.log(f"ledSettings: {ledSettings}", debug=True)
    # Define colors which will be used by the module.
    # Each color is an unsigned 32-bit value where the lower 24 bits define the red, green, blue data (each being 8 bits long).
#    self._DOT_COLORS=[Color(32,  0,  0,  0),   # red
#                      Color(32, 16,  0,  0),   # orange
#                      Color(32, 32,  0,  0),   # yellow
#                      Color( 0, 32,  0,  0),   # green
#                      Color( 0, 32, 32,  0),   # lightblue
#                      Color( 0,  0, 32,  0),   # blue
#                      Color(16,  0, 16,  0),   # purple
#                      Color(32,  0, 16,  0)]   # pink
    self._DOT_COLORS=[Color(255,   0,   0,  255),   # red
                      Color(255, 128,   0,  255),   # orange
                      Color(255, 255,   0,  255),   # yellow
                      Color(  0, 255,   0,  255),   # green
                      Color(  0, 255, 255,  255),   # lightblue
                      Color(  0,   0, 255,  255),   # blue
                      Color(128,   0, 128,  255),   # purple
                      Color(255,   0, 128,  255)]   # pink
    # Create a ws2811_t structure from the LED configuration.
    # Note that this structure will be created on the heap so you need to be careful
    # that you delete its memory by calling delete_ws2811_t when it's not needed.
    self._delayMilliseconds=75
    self._thread=None

  def run(self):
    self.log("starting the behavior in its own thread...", debug=True)
    offset=0
    # Initialize the ledstrip if that's not done yet:
    if self._ledSettings["strip"] == None:
      # PixelStrip.__init__(self, num, pin, freq_hz=800000, dma=10, invert=False, brightness=255, \
      #                           channel=0, strip_type=None, gamma=None):
      self._ledSettings["strip"]=PixelStrip(num=self._ledSettings["ledCount"], \
                  pin=self._ledSettings["stripGpioPin"], \
                  freq_hz=self._ledSettings["ledFrequency"], \
                  dma=self._ledSettings["ledDmaChannel"], \
                  invert=self._ledSettings["ledInvert"], \
                  brightness=self._ledSettings["ledBrightness"], \
                  channel=self._ledSettings["ledChannel"], \
                  strip_type=self._stripType)
      # Initialize the library (must be called once before other functions):
      self._ledSettings["strip"].begin()
    # Keep looping in the thread until the user switches off the lights:
    while self._ledSettings["lightState"]:
      # Update each LED color in the buffer.
      for i in range(self._ledSettings["ledCount"]):
        # Pick a color based on LED position and an offset for animation.
        color=self._DOT_COLORS[(i + offset) % len(self._DOT_COLORS)]
        # Set the LED color buffer value.
        self._ledSettings["strip"].setPixelColor(i, color)
        # Increase offset to animate colors moving.  Will eventually overflow, which is fine.
        offset += 1
      # Update the brightness of the leds:
#      self._ledSettings["strip"].setBrightness(self._ledSettings["ledBrightness"])
      self._ledSettings["strip"].setBrightness(255)
      # Force the ledstrip to show the applied changes:
      self._ledSettings["strip"].show()
      # Optionally slow down the loop:
      if self._delayMilliseconds > 0:
         sleep(self._delayMilliseconds / 1000)
    # The loop ended.
    self.log("ending Christmass thread...", debug=True)
    # Turn the leds off.
    # The color setting of each led needs to be set to 0:
    self.log("turn leds off", debug=True)
    color=Color(0, 0, 0, 0)
    for i in range(self._ledSettings["ledCount"]):
      self._ledSettings["strip"].setPixelColor(i, color)
    # Force the ledstrip to show the applied changes:
    self._ledSettings["strip"].show()

  def On(self):
    self.log("turning the leds on...")
    # The thread will loop for as long as the 'lightState' is true:
    self._ledSettings["lightState"]=True
    # Start the thread if not running yet:
    if self._thread == None:
      self.log("Creating a new thread", debug=True)
      self._thread=threading.Thread(target=self.run)
      self._thread.start()
    else:
      if not self._thread.isAlive():
        self.log("Need to start the thread", debug=True)
        self._thread=None
        self._thread=threading.Thread(target=self.run)
        self._thread.start()

  def Off(self):
    self.log("turning the leds off...")
    self._ledSettings["lightState"]=False
