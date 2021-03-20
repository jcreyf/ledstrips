#!/usr/bin/env python3
#***********************************************************************************************************#
# Bare basic app to drive a 7 meter LED strip with standard electrical light switches just like any         #
# ordinary light bulb in the house.  All leds on the strip just lighting up bright white or off.            #
#                                                                                                           #
# Led strips data line connected to pin 12 on the RPi (GPIO 18)                                             #
# Light switch 1 connected to pin 16 (GPIO 23) and pin 1 (3v3) to give it power through a 1.2kOhm resistor  #
# (this resistor is a lot smaller because of the leads to the switch being much longer than the other swith #
# and suffering from quite a significant voltage drop)                                                      #
# Light switch 2 connected to pin 18 (GPIO 24) and pin 17 (3v3) to give it power through a 12kOhm resistor  #
#***********************************************************************************************************#
from jcreyf_ledstrip import Light, Switch
from jcreyf_api import RESTserver
from time import sleep
import yaml
import sys
import os
import threading

# See if the DEBUG environment variable was set (false by default):
DEBUG=os.getenv('DEBUG', False)
if type(DEBUG) == str:
  DEBUG=DEBUG.lower() in ('true', 'yes', 'y', '1')

def debug(*args):
  """ Simple function to print messages to the console if the DEBUG-flag is set. """
  if DEBUG:
    # We don't want to print the message as a list between '()' if we only got 1 element in the argument list:
    if len(args) == 1:
      print(("debug -> {}").format(args[0]))
    else:
      print(("debug -> {}").format(args))

def apiGETLights(uri, path_vars, parms) -> str:
  """ Callback function for the GET operation at the '/lights' endpoint. """
  debug(uri)
  for path_var in path_vars:
    print(("  path variable = '{}': '{}'").format(path_var, path_vars[path_var]))
  for parm in parms:
    print(("  parameter     = '{}': '{}'").format(parm, parms[parm]))
  html="<h1>GET - Lights:</h1>"
  for light in lights:
    url=("/light/{}").format(light._name)
    html+=("<h3>{}</h3>Url: <a href='{}'>{}</a><br><br>").format(light._name, url, url)
  return html

def apiGETLight(uri, path_vars, parms) -> str:
  """ Callback function for the GET operation at the '/light/<light_name>' endpoint. """
  debug(uri)
  for path_var in path_vars:
    print(("  path variable = '{}': '{}'").format(path_var, path_vars[path_var]))
    if path_var == "light_name":
      light_name=path_vars[path_var]
  for parm in parms:
    print(("  parameter     = '{}': '{}'").format(parm, parms[parm]))
  html=("<h1>GET - Light {}:</h1>").format(light_name)
#  for switch in light.switches:
#    url=("/light/{}/switch").format(light._name)
#    html+=("<h3>{}</h3>Url: <a href='{}'>{}</a><br><br>").format(light._name, url, url)
  return html

def apiPOSTLight(uri, path_vars, parms) -> str:
  """ Callback function for the POST operation at the '/light/<light_name>' endpoint. """
  debug(uri)
  for path_var in path_vars:
    print(("  path variable = '{}': '{}'").format(path_var, path_vars[path_var]))
  for parm in parms:
    print(("  parameter     = '{}': '{}'").format(parm, parms[parm]))
#  self.Toggle()
  return ("POST - Toggled light {} - {}").format("self._name", "self._lightState")

def apiGETLightSwitches(uri, path_vars, parms) -> str:
  """ Callback function for the GET operation at the '/light/<light_name>/switches' endpoint. """
  debug(uri)
  for path_var in path_vars:
    print(("  path variable = '{}': '{}'").format(path_var, path_vars[path_var]))
  for parm in parms:
    print(("  parameter     = '{}': '{}'").format(parm, parms[parm]))
  return "GET - Light Switches"

def apiGETLightSwitch(uri, path_vars, parms) -> str:
  """ Callback function for the GET operation at the '/light/<light_name>/switch/<switch_name>' endpoint. """
  debug(uri)
  for path_var in path_vars:
    print(("  path variable = '{}': '{}'").format(path_var, path_vars[path_var]))
  for parm in parms:
    print(("  parameter     = '{}': '{}'").format(parm, parms[parm]))
  return "GET - Light Switch"


#--------------------------------------------------#
# The app starts here...
#--------------------------------------------------#
if __name__ == '__main__':
  print(("number of threads: {}").format(threading.activeCount()))
  print("Reading the config...")
  apiServer=None        # the REST API server wrapper
  lights=[]             # list of Light objects (typically 1)

  # We run this app as a daemon on the Raspberry PI, which means that we most probably run this from a different
  # directory.  The lights.yaml file is in the same directory as this app, so make sure we explicitly set the
  # directory before trying to open the file:
  _dir=os.path.dirname(__file__)
  if not _dir == "":
    print("Running this in directory: "+_dir)
    os.chdir(_dir)

  # Now open the yaml config-file and read it:
  with open("lights.yaml", 'r') as stream:
    try:
      config=yaml.safe_load(stream)
    except yaml.YAMLError as exc:
      print(exc)
      sys.exit(1)

  # There may be config for multiple lights in the yaml-file.
  # Lets set them all up:
  debug(("config: {}").format(config))

  # The API server is optional:
  try:
    apiserver_config=config["apiserver"]
    _name=apiserver_config["name"]
    _port=apiserver_config["port"]
    print("API Server:")
    print(" name:", _name)
    print(" port:", _port)
    apiServer=RESTserver(_name)
    apiServer.debug=DEBUG
    apiServer.port=_port
    del apiserver_config   # No longer need this config in memory
    del _name
    del _port
  except:
    print("there's no config for an API server")

  lights_config=config["lights"]
  debug(("Number of light configurations: {}").format(len(lights_config)))
  print("===================")
  for light_config in lights_config:
    print("Light:")
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
    _light=Light(_name)
    _light.debug=DEBUG
    _light.ledCount=_ledCount
    _light.ledBrightness=_brightness
    _light.stripGpioPin=_gpioPin
    _light.Start()

    # Each light may have 0 or more switches to control it.
    try:
      switches_config=light_config['switches']
      # This handles the case when a 'switches' section is added to the yaml-file but no 'switch' items:
      if switches_config is None:
        switches_config=[]
    except:
      # There's no configuration for switches.  That's fine!
      switches_config=[]

    if len(switches_config) == 0:
      print("there are no switches configured for this light")
    else:
      # Lets set them all up for this light:
      for switch_config in switches_config:
        print(" switch:")
        debug(("switch config: {}").format(switch_config))
        _name=switch_config['name']
        _gpioPin=switch_config['gpio_pin']
        print("  name:", _name)
        print("  GPIO pin:", _gpioPin)
        # Create the switch and set its properties:
        _switch=Switch(_name)
        _switch.gpioPin=_gpioPin
        _switch.init()
        _light.addSwitch(_switch)

    # Add the light to the list and move on to the next one (if any)
    lights.append(_light)

  # Everything has been set up.  No longer need these config objects in memory:
  # (this app is running for months or even years without reboots on a resource limited device)
  del _name
  del _gpioPin
  del _ledCount
  del _brightness
  del _switch
  del _light
  del switch_config
  del switches_config
  del light_config
  del lights_config
  del config

  # List the Lights and their Switch objects (if any):
  if DEBUG:
    print("---------------")
    for light in lights:
      debug(("Light object: {}").format(light.name))
      for switch in light.switches:
        debug(("  Switch object: {}").format(switch.name))
    print("---------------")

  print("===================")
  # The API server is optional, so don't try to configure and start one if we don't have one set up:
  if isinstance(apiServer, RESTserver):
    print("Setting up routing rules in the API server...")
    #  allowedMethods=['GET','POST','PUT','DELETE',])

    # View the whole setup: http://0.0.0.0:80/
    print("  setting up: /")
    apiServer.add_endpoint(endpoint='/', \
                           endpoint_name='home', \
                           htmlTemplateFile='home.html', \
                           htmlTemplateData={'title': 'Ledstrip', \
                                             'name': '<oops>', \
                                             'switches': '[oops]'}, \
                           allowedMethods=['GET',])
    # View all the Light objects in the setup: http://0.0.0.0:80/lights
    print("  setting up: /lights")
    apiServer.add_endpoint(endpoint='/lights', \
                           endpoint_name='lights', \
                           getHandler=apiGETLights, \
                           allowedMethods=['GET',])
    # View the setup of 1 specific Light object: http://0.0.0.0:80/light/<name>
    # 'GET' shows the config;
    # 'POST' to update its config (config in body as JSON payload);
    print("  setting up: /light/<light_name>")
    apiServer.add_endpoint(endpoint='/light/<light_name>', \
                           endpoint_name='light', \
                           getHandler=apiGETLight, \
                           postHandler=apiPOSTLight, \
                           allowedMethods=['GET','POST',])
    # View all the Switch objects in the setup for a specific Light: http://0.0.0.0:80/light/<name>/switches
    print("  setting up: /light/<light_name>/switches")
    apiServer.add_endpoint(endpoint='/light/<light_name>/switches', \
                           endpoint_name='switches', \
                           getHandler=apiGETLightSwitches, \
                           allowedMethods=['GET',])
    # View the setup of 1 specific Switch object for a specific Light: http://0.0.0.0:80/light/<name>/switch/<name>
    print("  setting up: /light/<light_name>/switch/<switch_name>")
    apiServer.add_endpoint(endpoint='/light/<light_name>/switch/<switch_name>', \
                           endpoint_name='switch', \
                           getHandler=apiGETLightSwitch, \
                           allowedMethods=['GET',])

    print("Starting the REST API server...")
    apiServer.start()

  print('Press Ctrl-C to quit.')

  try:
    while True:
      # Infinite loop, checking each button status every so many milliseconds and toggling the lights
      # if a change in one of the switches is detected:
      sleep(0.5)
      debug("checking switches...")
      for light in lights:
        for switch in light.switches:
          if switch.hasChanged():
            debug(("switch {} event -> toggling light {}").format(switch.name, light.name))
            light.Toggle()

  except KeyboardInterrupt:
    # Ctrl-C was hit!
    print("...ending app...")

  finally:
    # Destroy the objects, invoking their destructors, which will turn off the light and clean up all the resources:
    del apiServer
    for light in lights:
      for switch in light.switches:
        debug(("destroying switch: {}").format(switch.name))
        light.delSwitch(switch)
      debug(("destroying light: {}").format(light.name))
      del light
    # Release the ports that were setup on the RPi for this app:
    Switch.cleanUp()
    # Then stop the app...
    print("I'm out of here! Adios...\n")