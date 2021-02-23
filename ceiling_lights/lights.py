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

class Light:
    """
    Class that represents a LED light strip connected to a Raspberry PI through a single I/O port.
    Data going through that I/O port and power supplied externally (because it's too much for the PI
    to power them if there are too many).
    """
    def __init__(self, name):
        """
        Constructor, initializing members with default values.
        """
        print("creating light object: "+name)
        self._name=name              # Human name of the LED strip;
        self._ledCount=100           # Number of individually addressable LEDs on the strip;
        self._ledBrightness=128      # Set to 0 for darkest and 255 for brightest;
        self._ledFrequency=800000    # LED signal frequency in hertz (usually 800khz);
        self._ledDmaChannel=10       # DMA channel to use for generating signal (try 10);
        self._ledInvert=False        # True to invert the signal (when using NPN transistor level shift);
        self._ledChannel=0
        self._stripGpioPin=18        # RaspberryPI GPIO pin that is used to drive the LED strip;
        self._stripType=ws.SK6812_STRIP_RGBW
        self._strip=None             # instance of the rpi_ws281x LED strip;
        self._lightState=False       # Is the light "off" (false) or "on" (true);

    def __del__(self):
        """
        Destructor will turn off the lights.
        """
        print("destroying light object: "+self._name)
        self.Off()

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name=value

    @property
    def ledCount(self):
        return self._ledCount
    
    @ledCount.setter
    def ledCount(self, value):
        if not (value > 0): raise Exception("You need to have at least 1 LED on the strip!")
        self._ledCount=value

    @property
    def ledBrightness(self):
        return self._ledBrightness
    
    @ledBrightness.setter
    def ledBrightness(self, value):
        if not ((value > 0) and (value <= 255)): raise Exception("Brightness needs to be between 1 and 255!")
        self._ledBrightness=value

    @property
    def stripGpioPin(self):
        return self._stripGpioPin

    @stripGpioPin.setter
    def stripGpioPin(self, value):
        # The number of valid GPIO ports is limited and specific.
        # A good validator should check the port based on RPi model and throw an exception if the
        # selected port does not work to drive a LED strip like these.
        # I've decided to have a very rough validator here that enforces a port between 2 and 26.
        # I know this is not a great validator and I should probably make it more specific at some point.
        if not ((value >= 2) and (value <= 26)): raise Exception("The RPi GPIO port needs to be between 2 and 26!")
        self._stripGpioPin=value

    def state(self):
        """
        Show if the light is currently on or off.
        "True" means "On" and "False" means "Off".
        """
        return self._lightState

    def Start(self):
        """
        Initialize the LED strip at the hardware level so that we can start control the individual LEDs.
        """
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
        """
        Turn on the leds
        """
        # Set the leds to white, full brightness:
        color = Color(0, 0, 0, 255)
        for i in range(self._strip.numPixels()):
            self._strip.setPixelColor(i, color)
        self._strip.show()
        self._lightState=True

    def Off(self):
        """
        Turn off the leds
        """
        color = Color(0, 0, 0, 0)
        for i in range(self._strip.numPixels()):
            self._strip.setPixelColor(i, color)
        self._strip.show()
        self._lightState=False
    
    def Toggle(self):
        """
        Toggle the light on or off
        """
        if self._lightState:
            self.Off()
        else:
            self.On()


class Switch:
    """
    Class that represents a typical and standard on/off toggle switch connected to a Raspberry PI.
    """
    def __init__(self, name):
        """
        Constructor setting some default values.
        """
        print("creating switch object: "+name)
        self._state=False
        self._name=name
        self._gpioPin=0

    def __del__(self):
        """
        Destructor to release and clean up GPIO resources.
        """
        print("destroying switch object: "+self._name)
        GPIO.cleanup()

    @property
    def state(self):
        """
        Get the actual current state of the switch from the GPIO port.
        """
        self._state=GPIO.input(self._gpioPin)
        return self._state

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name=value

    @property
    def gpioPin(self):
        return self._gpioPin

    @gpioPin.setter
    def gpioPin(self, value):
        # The number of valid GPIO ports is limited and specific.
        # A good validator should check the port based on RPi model and throw an exception if the
        # selected port does not work to drive a LED strip like these.
        # I've decided to have a very rough validator here that enforces a port between 2 and 26.
        # I know this is not a great validator and I should probably make it more specific at some point.
        if not ((value >= 2) and (value <= 26)): raise Exception("The RPi GPIO port needs to be between 2 and 26!")
        self._gpioPin=value

    def hasChanged(self):
        """
        Method to detect if the state of the switch has changed since last time we checked.
        """
        if self._state != self.state():
            return True
        else:
            return False

    def init(self):
        """
        Method to initialize the hardware at GPIO level.
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._gpioPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


#--------------------------------------------------#
# The app starts here...
#--------------------------------------------------#
if __name__ == '__main__':
    print('Press Ctrl-C to quit.')

    # Create a light instance and set its properties:
    # (215 leds on a single strip, connected to RPi GPIO 18 (pin 12))
    light1=Light("Loft")
    light1.ledCount=215
    light1.ledBrightness=255
    light1.stripGpioPin=18
    light1.Start()

    # Create the switches:
    # switch 1 connected to pin 16 (GPIO 23) and pin 1 (3v3) to give it power through a 12kOhm resistor
    switchDownstairs=Switch("DownStairs")
    switchDownstairs.gpioPin=23
    switchDownstairs.init()
    # switch 2 connected to pin 18 (GPIO 24) and pin 17 (3v3) to give it power through a 12kOhm resistor:
    switchUpstairs=Switch("UpStairs")
    switchUpstairs.gpioPin=24
    switchUpstairs.init()

    try:
        while True:
            # Infinite loop, checking the button status every so many milliseconds and toggling the light
            # if a change in one of the switches is detected:
            sleep(0.5)
            if switchDownstairs.hasChanged() or switchUpstairs.hasChanged():
                light1.Toggle()

    except KeyboardInterrupt:
        # Ctrl-C was hit!
        # Destroy the objects, invoking their destructors, which will turn off the light and clean up all the resources.
        # Then stop the app...
        del switchUpstairs
        del switchDownstairs
        del light1