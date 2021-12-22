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

from rpi_ws281x import Color, PixelStrip, ws
from time import sleep
import threading


#
#----------------------------------
#
class BehaviorModule(threading.Thread):
  """
  Template Class for ledstrip behavior modules.
  """
  def __init__(self, name: str="Blank", ledSettings: dict=None):
    """ Constructor """
    threading.Thread.__init__(self)
    self._name=name
    self._ledSettings=ledSettings
    # The type of the LED strip (just RGB or does it also include a White LED);
    self._stripType=ws.SK6812_STRIP_RGBW
    print(f"BehaviorModule '{self._name}': Constructor")

  def __del__(self):
    """ Destructor will turn off the leds. """
    print(f"BehaviorModule '{self._name}': Destructor")

  @property
  def name(self):
    """ Return the name of this behavior module. """
    return self._name

  def run(self):
    """ Method that is called when the thread starts. """
    print(f"BehaviorModule '{self._name}': Starting thread")

  def On(self):
    """ Method to start the behavior. """
    print(f"BehaviorModule '{self._name}': Starting behavior...")

  def Off(self):
    """ Method to stop the behavior. """
    print(f"BehaviorModule '{self._name}': Stopping the behavior...")

  def Finalize(self):
    """ Destructor method to release and cleanup resources. """
    print(f"BehaviorModule '{self._name}': Finalizing behavior...")


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

  def run(self):
    print(f"BehaviorModule '{self._name}': starting the behavior...")

  def On(self):
    print(f"BehaviorModule '{self._name}': turning the leds on...")
    self._ledSettings["lightState"]=True
    self.Code()

  def Off(self):
    print(f"BehaviorModule '{self._name}': turning the leds off...")
    self._ledSettings["lightState"]=False
    self.Code()

  def Finalize(self):
    print(f"BehaviorModule '{self._name}': cleaning up resources...")

  def Code(self):
    print(f"BehaviorModule '{self._name}': Settings -> \n{self._ledSettings")
    # Initialize the ledstrip if that's not done yet:
    if self._ledSettings["strip"] == None:
      self._ledSettings["strip"]=PixelStrip(self._ledSettings["ledCount"], \
                  self._ledSettings["stripGpioPin"], \
                  self._ledSettings["ledFrequency"], \
                  self._ledSettings["ledDmaChannel"], \
                  self._ledSettings["ledInvert"], \
                  self._ledSettings["ledBrightness"], \
                  self._ledSettings["ledChannel"], \
                  super()._stripType)
      # Initialize the library (must be called once before other functions):
      self._ledSettings["strip"].begin()
    if self._ledSettings["lightState"]:
      # The light is on -> turn the leds off:
      color=Color(0, 0, 0, 0)
    else:
      # The light is off -> set the led color and brightness:
      color=Color(self._ledSettings["greenRGB"], \
                  self._ledSettings["redRGB"], \
                  self._ledSettings["blueRGB"], \
                  self._ledSettings["ledBrightness"])
    # Loop and set all leds on the strip:
    for i in range(self._ledSettings["strip"].numPixels()):
      self._ledSettings["strip"].setPixelColor(i, color)
    # Execute:
    self._ledSettings["strip"].show()


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
  
  def run(self):
    print(f"BehaviorModule '{self._name}': starting the behavior...")

  def On(self):
    print(f"BehaviorModule '{self._name}': turning the leds on...")
    self._ledSettings["lightState"]=True
#    mod=threading.Thread(target=self.Christmass_Code)
#    mod.start()
    print("Turning on (Christmass thread started)")

  def Off(self):
    print(f"BehaviorModule '{self._name}': turning the leds off...")
    self._ledSettings["lightState"]=False
    print("Turning off (this should end the Christmass thread)")

  def Finalize(self):
    print(f"BehaviorModule '{self._name}': cleaning up resources...")

  def Christmass_Code(self, stop: bool=False):
    print(f"BehaviorModule '{self._name}': start of thread")
    # Define colors which will be used by the module.
    # Each color is an unsigned 32-bit value where the lower 24 bits define the red, green, blue data (each being 8 bits long).
    DOT_COLORS=[0x200000,   # red
                0x201000,   # orange
                0x202000,   # yellow
                0x002000,   # green
                0x002020,   # lightblue
                0x000020,   # blue
                0x100010,   # purple
                0x200010]   # pink
    if self._ledSettings["strip"] == None:
      self._ledSettings["strip"]=ws.SK6812W_STRIP
    # Create a ws2811_t structure from the LED configuration.
    # Note that this structure will be created on the heap so you need to be careful
    # that you delete its memory by calling delete_ws2811_t when it's not needed.
    leds=ws.new_ws2811_t()
    # Initialize all channels to off
    for channum in range(2):
      channel=ws.ws2811_channel_get(leds, channum)
      ws.ws2811_channel_t_count_set(channel, 0)
      ws.ws2811_channel_t_gpionum_set(channel, 0)
      ws.ws2811_channel_t_invert_set(channel, 0)
      ws.ws2811_channel_t_brightness_set(channel, 0)

    channel=ws.ws2811_channel_get(leds, self._ledSettings["ledChannel"])
    ws.ws2811_channel_t_count_set(channel, self._ledSettings["ledCount"])
    ws.ws2811_channel_t_gpionum_set(channel, self._ledSettings["stripGpioPin"])
    ws.ws2811_channel_t_invert_set(channel, self._ledSettings["ledInvert"])
    ws.ws2811_channel_t_brightness_set(channel, self._ledSettings["ledBrightness"])
    ws.ws2811_channel_t_strip_type_set(channel, self._ledSettings["strip"])
    ws.ws2811_t_freq_set(leds, self._ledSettings["ledFrequency"])
    ws.ws2811_t_dmanum_set(leds, self._ledSettings["ledDmaChannel"])
    # Initialize library with LED configuration.
    resp=ws.ws2811_init(leds)
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
          color=DOT_COLORS[(i + offset) % len(DOT_COLORS)]
          # Set the LED color buffer value.
          ws.ws2811_led_set(channel, i, color)
          # Send the LED color data to the hardware.
          resp=ws.ws2811_render(leds)
          if resp != ws.WS2811_SUCCESS:
            message=ws.ws2811_get_return_t_str(resp)
            raise RuntimeError(f"ws2811_render failed with code {resp} ({message})")
          # Delay for a small period of time.
#          sleep(0.25)
          # Increase offset to animate colors moving.  Will eventually overflow, which is fine.
          offset += 1
      # The loop ended.
      print(f"BehaviorModule '{self._name}': end of thread")
      # Turn all the leds off:
      for i in range(self._ledSettings["ledCount"]):
        ws.ws2811_led_set(channel, i, 0)
        ws.ws2811_render(leds)
    finally:
      print(f"BehaviorModule '{self._name}': cleanup...")
      # Ensure ws2811_fini is called before the program quits.
      ws.ws2811_fini(leds)
      # Example of calling delete function to clean up structure memory.  Isn't
      # strictly necessary at the end of the program execution here, but is good practice.
      ws.delete_ws2811_t(leds)
