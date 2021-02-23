#!/usr/bin/env python3
#***********************************************************************************************************#
# Bare basic app to drive a 7 meter LED strip with a standard electrical light switches just like any       #
# ordinary light bulb in the house.  All leds on the strip just lighting up bright white or off.            #
#                                                                                                           #
# Led strips data line connected to pin 12 on the RPi (GPIO 18)                                             #
# Light switch 1 connected to pin 16 (GPIO 23) and pin 1 (3v3) to give it power through a 12kOhm resistor   #
# Light switch 2 connected to pin 18 (GPIO 24) and pin 17 (3v3) to give it power through a 12kOhm resistor  #
#***********************************************************************************************************#
from jcreyf_ledstrip import Light, Switch

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

    finally:
        # Clean up the Raspberry PI ports
        GPIO.cleanup()
        print("I'm out of here!  Adios...\n")