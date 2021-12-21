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

from RPi import GPIO
from rpi_ws281x import Color, PixelStrip, ws
from time import sleep
import threading


class Light:
  """
  Class that represents a LED light strip connected to a Raspberry PI through a single I/O port.
  Data going through that I/O port and power supplied externally (because it's too much for the PI
  to power them if there are too many).
  """

  def __init__(self, name: str):
    """ Constructor, initializing members with default values. """
    print("  ..creating light object: "+name)
    self._name=name                        # Human name of the LED strip;
    self._ledCount=100                     # Number of individually addressable LEDs on the strip;
    self._redRGB=1                         # RGB Red color value;
    self._greenRGB=1                       # RGB Green color value;
    self._blueRGB=1                        # RGB Blue color value;
    self._ledBrightness=255                # Set to 0 for darkest and 255 for brightest;
    self._ledFrequency=800000              # LED signal frequency in hertz (usually 800khz);
    self._ledDmaChannel=10                 # DMA channel to use for generating signal (try 10);
    self._ledInvert=False                  # True to invert the signal (when using NPN transistor level shift);
    self._ledChannel=0
    self._stripGpioPin=18                  # RaspberryPI GPIO pin that is used to drive the LED strip;
    self._stripType=ws.SK6812_STRIP_RGBW   # The type of the LED strip (just RGB or does it also include a White LED);
    self._strip=None                       # Instance of the rpi_ws281x LED strip;
    self._lightState=False                 # Is the light "off" (false) or "on" (true);
    self._switches=[]                      # Optional list of Switch objects that are linked to this light object;
    self._debug=False                      # Debug level logging;
    self._behaviorModule="Default"         # Name of the module that has the code to turn the leds on/off

  def __del__(self):
    """ Destructor will turn off this light. """
    print("destroying light object: "+self._name)
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
    return self._ledCount
  
  @ledCount.setter
  def ledCount(self, value: int):
    """ Set the number of LEDs to use on this light strip.  You can activate fewer than available. """
    if not (value > 0): raise Exception("You need to have at least 1 LED on the strip!")
    self._ledCount=value

  @property
  def redRGB(self) -> int:
    """ Return the current Red RGB color value for the light strip. """
    return self._redRGB
  
  @redRGB.setter
  def redRGB(self, value: int):
    """ Set the red RGB color value of LEDs to use on this light strip. """
    if not ((value >= 0) and (value <= 255)): raise Exception("The red RGB value needs to be between 0 and 255!")
    self._redRGB=value

  @property
  def greenRGB(self) -> int:
    """ Return the current Green RGB color value for the light strip. """
    return self._greenRGB
  
  @greenRGB.setter
  def greenRGB(self, value: int):
    """ Set the green RGB color value of LEDs to use on this light strip. """
    if not ((value >= 0) and (value <= 255)): raise Exception("The green RGB value needs to be between 0 and 255!")
    self._greenRGB=value

  @property
  def blueRGB(self) -> int:
    """ Return the current Blue RGB color value for the light strip. """
    return self._blueRGB
  
  @blueRGB.setter
  def blueRGB(self, value: int):
    """ Set the blue RGB color value of LEDs to use on this light strip. """
    if not ((value >= 0) and (value <= 255)): raise Exception("The blue RGB value needs to be between 0 and 255!")
    self._blueRGB=value

#  @property
#  def ledColor(self) -> str:
#    """ Return the RGB color value of the LEDs. """
#    return self._ledColor
#
#  @ledColor.setter
#  def ledColor(self, value: str):
#    """ Set the RGB color value of the LEDs. """
#    self._ledColor=value

  @property
  def ledBrightness(self) -> int:
    """ Return the brightness that the LED have been configured with (0 to 255). """
    return self._ledBrightness
  
  @ledBrightness.setter
  def ledBrightness(self, value: int):
    """ Set the brightness of the LEDs (0 to 255). """
    if not ((value > 0) and (value <= 255)): raise Exception("Brightness needs to be between 1 and 255!")
    self._ledBrightness=value

  @property
  def stripGpioPin(self) -> int:
    """ Return the Raspberry PI GPIO pin the LED strip is connected to (data). """
    return self._stripGpioPin

  @stripGpioPin.setter
  def stripGpioPin(self, value: int):
    """ Set the Raspberry PI GPIO pin the LED strip is connected to (data). """
    # The number of valid GPIO ports is limited and specific.
    # A good validator should check the port based on RPi model and throw an exception if the
    # selected port does not work to drive a LED strip like these.
    # I've decided to have a very rough validator here that enforces a port between 2 and 26.
    # I know this is not a great validator and I should probably make it more specific at some point.
    if not ((value >= 2) and (value <= 26)): raise Exception("The RPi GPIO port needs to be between 2 and 26!")
    self._stripGpioPin=value

  @property
  def state(self) -> bool:
    """ Show if the light is currently on or off.  "True" means "On" and "False" means "Off". """
    return self._lightState

  @property
  def debug(self) -> bool:
    """ Return the debug-flag that is set for this light. """
    return self._debug

  @debug.setter
  def debug(self, flag: bool):
    """ Set the debug level. """
    self._debug=flag

  @property
  def behaviorModule(self):
    """ Return the name of the behavior module to run. """
    return self._behaviorModule
  
  @name.setter
  def behaviorModule(self, value: str):
    """ Set the name for the behavior module to run. """
    self._behaviorModule=value

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

  def Start(self):
    """ Initialize the LED strip at the hardware level so that we can start control the individual LEDs. """
#    self._strip=PixelStrip(self._ledCount, \
#                self._stripGpioPin, \
#                self._ledFrequency, \
#                self._ledDmaChannel, \
#                self._ledInvert, \
#                self._ledBrightness, \
#                self._ledChannel, \
#                self._stripType)
#    # Initialize the library (must be called once before other functions):
#    self._strip.begin()
    print("jcreyf_ledstrip.Start() called!!!")

  def On(self):
    """ Turn the leds on. """
    if self._behaviorModule == "Default":
      # Basic On behavior:
      self.Default_On()
    else:
      # Christmass party:
      self.Christmass_On()

  def Off(self):
    """ Turn the leds off. """
    if self._behaviorModule == "Default":
      # Basic Off behavior:
      self.Default_Off()
    else:
      # Christmass party:
      self.Christmass_Off()
  
  def Toggle(self):
    """ Toggle the light on or off. """
    if self._lightState:
      self.Off()
    else:
      self.On()

  def Update(self):
    """ Apply the Updated LED settings if they are on. """
    if self._lightState:
      self.Off()
      self.On()

#********** THE BELOW METHODS NEED TO MOVE INTO MODULES *********
  def Default_On(self):
    """ Turn the leds on. """
    # Initialize the ledstrip if that's not done yet:
    if self._strip == None:
      self._strip=PixelStrip(self._ledCount, \
                  self._stripGpioPin, \
                  self._ledFrequency, \
                  self._ledDmaChannel, \
                  self._ledInvert, \
                  self._ledBrightness, \
                  self._ledChannel, \
                  self._stripType)
      # Initialize the library (must be called once before other functions):
      self._strip.begin()

    # Set the led color, full brightness:
    color=Color(self._greenRGB, self._redRGB, self._blueRGB, self._ledBrightness)
    for i in range(self._strip.numPixels()):
      self._strip.setPixelColor(i, color)
    self._strip.show()
    self._lightState=True

  def Default_Off(self):
    """ Turn the leds off. """
    color=Color(0, 0, 0, 0)
    for i in range(self._strip.numPixels()):
      self._strip.setPixelColor(i, color)
    self._strip.show()
    self._lightState=False

#---------------

  def Christmass_Code(self):
    print("Start of Christmass thread")
    self._strip=ws.SK6812W_STRIP
    # Define colors which will be used by the example.  Each color is an unsigned
    # 32-bit value where the lower 24 bits define the red, green, blue data (each
    # being 8 bits long).
    DOT_COLORS=[0x200000,   # red
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
    leds=ws.new_ws2811_t()
    # Initialize all channels to off
    for channum in range(2):
      channel=ws.ws2811_channel_get(leds, channum)
      ws.ws2811_channel_t_count_set(channel, 0)
      ws.ws2811_channel_t_gpionum_set(channel, 0)
      ws.ws2811_channel_t_invert_set(channel, 0)
      ws.ws2811_channel_t_brightness_set(channel, 0)

    channel=ws.ws2811_channel_get(leds, self._ledChannel)
    ws.ws2811_channel_t_count_set(channel, self._ledCount)
    ws.ws2811_channel_t_gpionum_set(channel, self._stripGpioPin)
    ws.ws2811_channel_t_invert_set(channel, self._ledInvert)
    ws.ws2811_channel_t_brightness_set(channel, self._ledBrightness)
    ws.ws2811_channel_t_strip_type_set(channel, self._strip)
    ws.ws2811_t_freq_set(leds, self._ledFrequency)
    ws.ws2811_t_dmanum_set(leds, self._ledDmaChannel)
    # Initialize library with LED configuration.
    resp=ws.ws2811_init(leds)
    if resp != ws.WS2811_SUCCESS:
      message=ws.ws2811_get_return_t_str(resp)
      raise RuntimeError('ws2811_init failed with code {0} ({1})'.format(resp, message))

    # Wrap following code in a try/finally to ensure cleanup functions are called after library is initialized.
    try:
      offset=0
      # Keep looping in the thread until the user switches off the lights:
      while self._lightState:
        # Update each LED color in the buffer.
        for i in range(self._ledCount):
          # Pick a color based on LED position and an offset for animation.
          color=DOT_COLORS[(i + offset) % len(DOT_COLORS)]
          # Set the LED color buffer value.
          ws.ws2811_led_set(channel, i, color)
          # Send the LED color data to the hardware.
          resp=ws.ws2811_render(leds)
          if resp != ws.WS2811_SUCCESS:
            message=ws.ws2811_get_return_t_str(resp)
            raise RuntimeError('ws2811_render failed with code {0} ({1})'.format(resp, message))
          # Delay for a small period of time.
#          sleep(0.25)
          # Increase offset to animate colors moving.  Will eventually overflow, which is fine.
          offset += 1
      # The loop ended.
      print("End of Christmass thread")
    finally:
      print("Christmass cleanup...")
      # Ensure ws2811_fini is called before the program quits.
      ws.ws2811_fini(leds)
      # Example of calling delete function to clean up structure memory.  Isn't
      # strictly necessary at the end of the program execution here, but is good practice.
      ws.delete_ws2811_t(leds)


  def Christmass_On(self):
    """ Turn the leds on. """
    # Remove the previous ledstrip object if that was set before switching to Christmass mode:
    if self._strip != None:
      self._strip=None

    self._lightState=True
    mod=threading.Thread(target=self.Christmass_Code)
    mod.start()

  def Christmass_Off(self):
    """ Turn the leds off. """
    self._lightState=False

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
    print("  ..creating switch object: "+name)
    self._state=True
    self._name=name
    self._gpioPin=0

  def __del__(self):
    """ Destructor to release and clean up GPIO resources. """
    print("destroying switch object: "+self._name)

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
