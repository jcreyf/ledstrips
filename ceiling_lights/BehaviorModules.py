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
class BehaviorModule(threading.Thread):
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
    threading.Thread.__init__(self)
    # Setting the name of the thread:
    self.name=name
    # ToDo: This _name is redundant and can probably be removed.
    #       This _name property was added to the initial code, before we started using threads
    #       to run behavior code.
    self._name=name
    self._debug=True
    self._ledSettings=ledSettings
    # The type of the LED strip (just RGB or does it also include a White LED);
    self._stripType=ws.SK6812_STRIP_RGBW
    self.log("Constructor")
    self.log(f"ledSettings: {ledSettings}", debug=True)

  def __del__(self):
    """ Destructor will turn off the leds. """
    self.log("Destructor")
    self.finalize()

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

  def run(self):
    """ Method that is called when the thread starts. """
    self.log(f"Starting thread in its own thread", debug=True)

  def On(self):
    """ Method to start the behavior. """
    self.log("On()")
    self.log(f"ledSettings: {self._ledSettings}", debug=True)

  def Off(self):
    """ Method to stop the behavior. """
    self.log("Off()")
    self.log(f"ledSettings: {self._ledSettings}", debug=True)

  def finalize(self):
    """ Destructor method to release and cleanup resources. """
    self.log("Finalizing and cleaning up resources...", debug=True)


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
      self._ledSettings["strip"]=PixelStrip(self._ledSettings["ledCount"], \
                  self._ledSettings["stripGpioPin"], \
                  self._ledSettings["ledFrequency"], \
                  self._ledSettings["ledDmaChannel"], \
                  self._ledSettings["ledInvert"], \
                  self._ledSettings["ledBrightness"], \
                  self._ledSettings["ledChannel"], \
                  self._stripType)
      # Initialize the library (must be called once before other functions):
      self._ledSettings["strip"].begin()
    if state:
      # Turn the leds on.
      # Generate the color setting for each led:
      color=Color(self._ledSettings["greenRGB"], \
                  self._ledSettings["redRGB"], \
                  self._ledSettings["blueRGB"], \
                  self._ledSettings["ledBrightness"])
      self.log("turn leds on", debug=True)
    else:
      # Turn the leds off.
      # The color setting of each led needs to be set to 0:
      color=Color(0, 0, 0, 0)
      self.log("turn leds off", debug=True)
    # Loop and apply the color setting to all leds on the strip:
    for i in range(self._ledSettings["strip"].numPixels()):
      self._ledSettings["strip"].setPixelColor(i, color)
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
    self._DOT_COLORS=[0x200000,   # red
                      0x201000,   # orange
                      0x202000,   # yellow
                      0x002000,   # green
                      0x002020,   # lightblue
                      0x000020,   # blue
                      0x100010,   # purple
                      0x200010]   # pink
    # Create a ws2811_t structure from the LED configuration.
    # Note that this structure will be created on the heap so you need to be careful
    # that you delete its memory by calling delete_ws2811_t when it's not needed.
    self._leds=ws.new_ws2811_t()
  
  def run(self):
    self.log("starting the behavior in its own thread...", debug=True)
#    if self._ledSettings["strip"] == None:
#      self._ledSettings["strip"]=ws.SK6812W_STRIP
    # Initialize all channels to off
    for channum in range(2):
      channel=ws.ws2811_channel_get(self._leds, channum)
      ws.ws2811_channel_t_count_set(channel, 0)
      ws.ws2811_channel_t_gpionum_set(channel, 0)
      ws.ws2811_channel_t_invert_set(channel, 0)
      ws.ws2811_channel_t_brightness_set(channel, 0)

    channel=ws.ws2811_channel_get(self._leds, self._ledSettings["ledChannel"])
    ws.ws2811_channel_t_count_set(channel, self._ledSettings["ledCount"])
    ws.ws2811_channel_t_gpionum_set(channel, self._ledSettings["stripGpioPin"])
    ws.ws2811_channel_t_invert_set(channel, self._ledSettings["ledInvert"])
    ws.ws2811_channel_t_brightness_set(channel, self._ledSettings["ledBrightness"])
    ws.ws2811_channel_t_strip_type_set(channel, self._ledSettings["strip"])
    ws.ws2811_t_freq_set(self._leds, self._ledSettings["ledFrequency"])
    ws.ws2811_t_dmanum_set(self._leds, self._ledSettings["ledDmaChannel"])
    # Initialize library with LED configuration.
    resp=ws.ws2811_init(self._leds)
    if resp != ws.WS2811_SUCCESS:
      message=ws.ws2811_get_return_t_str(resp)
      raise RuntimeError('ws2811_init failed with code {0} ({1})'.format(resp, message))

    # Wrap following code in a try/finally to ensure cleanup functions are called after library is initialized.
    try:
      offset=0
      # Keep looping in the thread until the user switches off the lights:
      while self._ledSettings["lightState"]:
        # Update each LED color in the buffer.
        for i in range(self._ledSettings["ledCount"]):
          # Pick a color based on LED position and an offset for animation.
          color=self._DOT_COLORS[(i + offset) % len(self._DOT_COLORS)]
          # Set the LED color buffer value.
          ws.ws2811_led_set(channel, i, color)
          # Send the LED color data to the hardware.
          resp=ws.ws2811_render(self._leds)
          if resp != ws.WS2811_SUCCESS:
            message=ws.ws2811_get_return_t_str(resp)
            raise RuntimeError(f"ws2811_render failed with code {resp} ({message})")
          # Delay for a small period of time.
# ToDo: add a class parameter to configure the speed delay:
#          sleep(0.25) # 250 milliseconds
          # Increase offset to animate colors moving.  Will eventually overflow, which is fine.
          offset += 1
      # The loop ended.
      self.log("ending Christmass thread...", debug=True)
      # Turn all the leds off:
      for i in range(self._ledSettings["ledCount"]):
        ws.ws2811_led_set(channel, i, 0)
        ws.ws2811_render(self._leds)
    finally:
      # Clean up hardware resources
      self.finalize()

  def On(self):
    self.log("turning the leds on...")
    self._ledSettings["lightState"]=True

  def Off(self):
    self.log("turning the leds off...")
    self._ledSettings["lightState"]=False

  def finalize(self):
    self.log("cleaning up resources...")
    # Ensure ws2811_fini is called before the program quits.
    ws.ws2811_fini(self._leds)
    # Example of calling delete function to clean up structure memory.  Isn't
    # strictly necessary at the end of the program execution here, but is good practice.
    ws.delete_ws2811_t(self._leds)
