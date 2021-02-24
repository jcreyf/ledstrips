from RPi import GPIO
from rpi_ws281x import Color, PixelStrip, ws

class Light:
  """
  Class that represents a LED light strip connected to a Raspberry PI through a single I/O port.
  Data going through that I/O port and power supplied externally (because it's too much for the PI
  to power them if there are too many).
  """
  def __init__(self, name):
    """ Constructor, initializing members with default values. """
    print("creating light object: "+name)
    self._name=name                        # Human name of the LED strip;
    self._ledCount=100                     # Number of individually addressable LEDs on the strip;
    self._ledBrightness=128                # Set to 0 for darkest and 255 for brightest;
    self._ledFrequency=800000              # LED signal frequency in hertz (usually 800khz);
    self._ledDmaChannel=10                 # DMA channel to use for generating signal (try 10);
    self._ledInvert=False                  # True to invert the signal (when using NPN transistor level shift);
    self._ledChannel=0
    self._stripGpioPin=18                  # RaspberryPI GPIO pin that is used to drive the LED strip;
    self._stripType=ws.SK6812_STRIP_RGBW   # the type of the LED strip (just RGB or does it also include a White LED);
    self._strip=None                       # instance of the rpi_ws281x LED strip;
    self._lightState=False                 # Is the light "off" (false) or "on" (true);
    self._switches=[]                      # optional list of Switch objects that are linked to this light object;

  def __del__(self):
    """ Destructor will turn off this light. """
    print("destroying light object: "+self._name)
    self.Off()

  @property
  def name(self):
    """ Return the name of this light. """
    return self._name
  
  @name.setter
  def name(self, value):
    """ Set the name for this light. """
    self._name=value

  @property
  def ledCount(self):
    """ Return the number of individual LEDs on the light strip. """
    return self._ledCount
  
  @ledCount.setter
  def ledCount(self, value):
    """ Set the number of LEDs to use on this light strip.  You can activate fewer than available. """
    if not (value > 0): raise Exception("You need to have at least 1 LED on the strip!")
    self._ledCount=value

  @property
  def ledBrightness(self):
    """ Return the brightness that the LED have been configured with (0 to 255). """
    return self._ledBrightness
  
  @ledBrightness.setter
  def ledBrightness(self, value):
    """ Set the brightness of the LEDs (0 to 255). """
    if not ((value > 0) and (value <= 255)): raise Exception("Brightness needs to be between 1 and 255!")
    self._ledBrightness=value

  @property
  def stripGpioPin(self):
    """ Return the Raspberry PI GPIO pin the LED strip is connected to (data). """
    return self._stripGpioPin

  @stripGpioPin.setter
  def stripGpioPin(self, value):
    """ Set the Raspberry PI GPIO pin the LED strip is connected to (data). """
    # The number of valid GPIO ports is limited and specific.
    # A good validator should check the port based on RPi model and throw an exception if the
    # selected port does not work to drive a LED strip like these.
    # I've decided to have a very rough validator here that enforces a port between 2 and 26.
    # I know this is not a great validator and I should probably make it more specific at some point.
    if not ((value >= 2) and (value <= 26)): raise Exception("The RPi GPIO port needs to be between 2 and 26!")
    self._stripGpioPin=value

  @property
  def switches(self):
    """ Return a list of 0 or more Switch objects that have been mapped to this light. """
    return self._switches

  def addSwitch(self, switch):
    """ Add a new Switch object that can control this light. """
    self._switches.append(switch)

  def delSwitch(self, switch):
    """ Remove a switch from this light. """
    self._switches.remove(switch)
    del switch

  def state(self):
    """ Show if the light is currently on or off.  "True" means "On" and "False" means "Off". """
    return self._lightState

  def Start(self):
    """ Initialize the LED strip at the hardware level so that we can start control the individual LEDs. """
    self._strip=PixelStrip(self._ledCount, \
                self._stripGpioPin, \
                self._ledFrequency, \
                self._ledDmaChannel, \
                self._ledInvert, \
                self._ledBrightness, \
                self._ledChannel, \
                self._stripType)
    # Intialize the library (must be called once before other functions):
    self._strip.begin()

  def On(self):
    """ Turn on the leds. """
    # Set the leds to white, full brightness:
    color = Color(0, 0, 0, 255)
    for i in range(self._strip.numPixels()):
      self._strip.setPixelColor(i, color)
    self._strip.show()
    self._lightState=True

  def Off(self):
    """ Turn off the leds. """
    color = Color(0, 0, 0, 0)
    for i in range(self._strip.numPixels()):
      self._strip.setPixelColor(i, color)
    self._strip.show()
    self._lightState=False
  
  def Toggle(self):
    """ Toggle the light on or off. """
    if self._lightState:
      self.Off()
    else:
      self.On()


class Switch:
  """
  Class that represents a typical and standard on/off toggle switch connected to a Raspberry PI.
  """
  def __init__(self, name):
    """ Constructor setting some default values. """
    print("creating switch object: "+name)
    self._state=False
    self._name=name
    self._gpioPin=0

  def __del__(self):
    """ Destructor to release and clean up GPIO resources. """
    print("destroying switch object: "+self._name)

  @property
  def state(self):
    """ Return the actual current state of the switch from the Raspberry PI GPIO port. """
    self._state=GPIO.input(self._gpioPin)
    return self._state

  @property
  def name(self):
    """ Return the name that was set for this switch. """
    return self._name

  @name.setter
  def name(self, value):
    """ Set a name for this switch. """
    self._name=value

  @property
  def gpioPin(self):
    """ Return the Raspberry PI GPIO pin that is use to connect this switch to. """
    return self._gpioPin

  @gpioPin.setter
  def gpioPin(self, value):
    """ Set the Raspberry PI GPIO pin that is use to connect this switch to. """
    # The number of valid GPIO ports is limited and specific.
    # A good validator should check the port based on RPi model and throw an exception if the
    # selected port does not work to drive a LED strip like these.
    # I've decided to have a very rough validator here that enforces a port between 2 and 26.
    # I know this is not a great validator and I should probably make it more specific at some point.
    if not ((value >= 2) and (value <= 26)): raise Exception("The RPi GPIO port needs to be between 2 and 26!")
    self._gpioPin=value

  def hasChanged(self):
    """ Method to detect if the state of the switch has changed since last time we checked. """
    if self._state != self.state:
      return True
    else:
      return False

  def init(self):
    """ Method to initialize the Raspberry PI hardware at GPIO level. """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self._gpioPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

  def cleanUp():
    """ Static method to cleanup the GPIO ports that this app used on the RPi. """
    GPIO.cleanup()
