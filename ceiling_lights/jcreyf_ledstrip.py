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

from jcreyf_api import RESTserver
from RPi import GPIO
from rpi_ws281x import Color, PixelStrip, ws

class Light:
  """
  Class that represents a LED light strip connected to a Raspberry PI through a single I/O port.
  Data going through that I/O port and power supplied externally (because it's too much for the PI
  to power them if there are too many).
  """

  def __init__(self, name: str):
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
    self._stripType=ws.SK6812_STRIP_RGBW   # The type of the LED strip (just RGB or does it also include a White LED);
    self._strip=None                       # Instance of the rpi_ws281x LED strip;
    self._lightState=False                 # Is the light "off" (false) or "on" (true);
    self._switches=[]                      # Optional list of Switch objects that are linked to this light object;
    self._apiServerPort=None               # The network port on which to run the REST API server;
    self._apiServer=None                   # Instance of the API server dedicated to this light;
    self._debug=False                      # Debug level logging;

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
  def debug(self) -> bool:
    """ Return the debug-flag that is set for this light. """
    return self._debug

  @debug.setter
  def debug(self, flag: bool):
    """ Set the debug level. """
    self._debug=flag

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

  @property
  def apiServerPort(self) -> int:
    """ Return the number of the network port on which the REST API server to control this light object. """
    return self._apiServerPort
  
  @apiServerPort.setter
  def apiServerPort(self, value: int):
    """ Set the network port of the RESTful web server.  This is an integer between 1 and 65535. """
    if value < 1 or value > 65535: raise Exception("The server port should be between 1 and 65535!")
    self._apiServerPort=value

  def state(self) -> bool:
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
    # Initialize the library (must be called once before other functions):
    self._strip.begin()
    # Setup the REST server so we can control the lights over the network:
    print(("setting up the {} REST API server...").format(self._name))
    self._apiServer=RESTserver(self._name)
    self._apiServer.debug=self._debug
    self._apiServer.port=self._apiServerPort
    # View the whole setup: http://0.0.0.0:80/
    self._apiServer.add_endpoint(endpoint='/', endpoint_name='home', \
                                               htmlTemplateFile='home.html', \
                                               htmlTemplateData={'title': 'Ledstrip', \
                                                                 'name': self._name, \
                                                                 'switches': self._switches}, \
                                               allowedMethods=['GET',])
    # View all the Light objects in the setup: http://0.0.0.0:80/lights
    self._apiServer.add_endpoint(endpoint='/lights', endpoint_name='lights', \
                                                    getHandler=self.apiGETLights, \
                                                    allowedMethods=['GET',])
    # View the setup of 1 specific Light object: http://0.0.0.0:80/light/<name>
    # 'GET' shows the config;
    # 'POST' to update its config (config in body as JSON payload);
    self._apiServer.add_endpoint(endpoint='/light/<light_name>', endpoint_name='light', \
                                                    getHandler=self.apiGETLight, \
                                                    postHandler=self.apiPOSTLight, \
                                                    allowedMethods=['GET','POST',])
    # View all the Switch objects in the setup for a specific Light: http://0.0.0.0:80/light/<name>/switches
    self._apiServer.add_endpoint(endpoint='/light/<light_name>/switches', endpoint_name='switches', \
                                                    getHandler=self.apiGETLightSwitches, \
                                                    allowedMethods=['GET',])
    # View the setup of 1 specific Switch object for a specific Light: http://0.0.0.0:80/light/<name>/switch/<name>
    self._apiServer.add_endpoint(endpoint='/light/<light_name>/switch/<switch_name>', endpoint_name='switch', \
                                                    getHandler=self.apiGETLightSwitch, \
                                                    allowedMethods=['GET',])



#  allowedMethods=['GET','POST','PUT','DELETE',])
#    self._apiServer.add_endpoint(endpoint='/lichten/', defaults={'light_name': None})

    self._apiServer.start()

  def On(self):
    """ Turn the leds on. """
    # Set the leds to white, full brightness:
    color = Color(0, 0, 0, 255)
    for i in range(self._strip.numPixels()):
      self._strip.setPixelColor(i, color)
    self._strip.show()
    self._lightState=True

  def Off(self):
    """ Turn the leds off. """
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

  def apiGETLights(self) -> str:
    """ Callback function for the GET operation at the '/lights' endpoint. """
    return "GET - Lights"

  def apiGETLight(self) -> str:
    """ Callback function for the GET operation at the '/light/<light_name>' endpoint. """
    return ("My name is: {}<br>my state is: {}").format(self._name, self._lightState)

  def apiPOSTLight(self) -> str:
    """ Callback function for the POST operation at the '/light/<light_name>' endpoint. """
    self.Toggle()
    return ("POST - Toggled light {} - {}").format(self._name, self._lightState)

  def apiGETLightSwitches(self) -> str:
    """ Callback function for the GET operation at the '/light/<light_name>/switches' endpoint. """
    return "GET - Light Switches"

  def apiGETLightSwitch(self) -> str:
    """ Callback function for the GET operation at the '/light/<light_name>/switch/<switch_name>' endpoint. """
    return "GET - Light Switch"

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
    print("creating switch object: "+name)
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
