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
from flask import request
import yaml
import sys
import os
import threading
import json

# See if the DEBUG environment variable was set (false by default):
DEBUG=os.getenv('DEBUG', False)
if type(DEBUG) == str:
  DEBUG=DEBUG.lower() in ('true', 'yes', 'y', '1')


def log(*args, debug: bool=False):
  """ Simple function to log messages to the console. """
  _log=True
  if debug and not DEBUG:
    _log=False
  if _log:
    # We don't want to log the message as a list between '()' if we only got 1 element in the argument list:
    if len(args) == 1:
      print(f"lights: {args[0]}")
    else:
      print(f"lights: {args}")
    # We need to flush the stdout buffer in python for log statements to reach the Linux systemd journal:
    sys.stdout.flush()


#def apiGETHome(host_url, uri, path_vars, parms) -> str:
def apiGETHome(path_vars, request) -> str:
  """ Callback function for the GET operation at the '/' endpoint. """
  log(uri, debug=True)
  for path_var in path_vars:
    log(f"  path variable = '{path_var}': '{path_vars[path_var]}'")
  for arg in request.args:
    log(f"  argument     = '{arg}': '{request.args[arg]}'")
  html="<h1>Ceiling Lights:</h1>"
  for light in lights:
    url=f"/light/{light._name}"
    html+=f"<h3>{light._name}</h3>Url: <a href='{url}'>{url}</a><br><br>"
  return html


#def apiGETLights(host_url, uri, path_vars, parms) -> str:
def apiGETLights(path_vars, request) -> str:
  """ Callback function for the GET operation at the '/lights' endpoint.
  This returns a JSON object like this example:
  {
    "self": "http://localhost:8888/lights",
    "lights": [
        {
            "name": "Loft",
            "uri": "http://localhost:8888/light/Loft"
        },
        {
            "name": "Status",
            "uri": "http://localhost:8888/light/Status"
        }
    ]
  }
  """
  log(request.full_path, debug=True)
  for path_var in path_vars:
    log(f"  path variable = '{path_var}': '{path_vars[path_var]}'")
  for arg in request.args:
    log(f"  argument     = '{arg}': '{request.args[arg]}'")
  _returnValue={}
  # Remove leading or trailing slashes and questionmarks.
  # In real life, this is removing the leading slash and trailing questionmark
  _self=request.host_url+request.full_path.strip("/").strip("?")
  _returnValue["self"]=_self
  _lights=[]
  for light in lights:
    _lights.append({"name": light.name,
                    "uri": request.host_url+"light/"+light.name})
  _returnValue["lights"]=_lights
  return json.dumps(_returnValue)


#def apiGETLight(host_url, uri, path_vars, parms) -> str:
def apiGETLight(path_vars, request) -> str:
  """ Callback function for the GET operation at the '/light/<light_name>' endpoint.
  This returns a JSON object like this example:
  {
    "self": "http://192.168.1.12:8888/light/Bureau",
    "light": {
      "name": "Bureau",
      "uri": "http://192.168.1.12:8888/light/Bureau",
      "state": false,
      "color": {
        "red": 1,
        "green": 1,
        "blue": 1
      },
      "brightness": 255
    },
    "switches": [
      {
        "name": "Desk",
        "uri": "http://192.168.1.12:8888/light/Bureau/switch/Desk",
        "state": 1
      }
    ]
  }
"""
  log(request.full_path, debug=True)
  for path_var in path_vars:
    log(f"  path variable = '{path_var}': '{path_vars[path_var]}'")
    if path_var == "light_name":
      light_name=path_vars[path_var]
  for arg in request.args:
    log(f"  argument     = '{arg}': '{request.args[arg]}'")
  _returnValue={}
  # Remove leading or trailing slashes and questionmarks.
  # In real life, this is removing the leading slash and trailing questionmark
  _self=request.host_url+request.full_path.strip("/").strip("?")
  _returnValue["self"]=_self
  # Go find the light:
  _found=False
  for light in lights:
    if light.name == light_name:
      _found=True
      break
  if _found:
    # We found the light.  Generate the payload to send back with the light's details:
    _returnValue["light"]={"name": light.name,
                           "uri": request.host_url+f"light/{light.name}",
                           "state": light.state,
                           "color": {
                             "red": light.redRGB,
                             "green": light.greenRGB,
                             "blue": light.blueRGB
                           },
                           "brightness": light.ledBrightness
                          }
    _switches=[]
    for switch in light.switches:
      _switches.append({"name": switch.name,
                        "uri": request.host_url+f"light/{light.name}/switch/{switch.name}",
                        "state": switch._state
                       })
    _returnValue["switches"]=_switches
  else:
    # We can't find this light!  Oops...
    _errors=[]
    _errors.append({"error": f"Light {light_name} not found!"})
    _returnValue["errors"]=_errors
  return json.dumps(_returnValue)


#def apiPOSTLight(host_url, uri, path_vars, parms) -> str:
def apiPOSTLight(path_vars, request) -> str:
  """ Callback function for the POST operation at the '/light/<light_name>' endpoint.
  We assume a JSON payload like this:
  {
  	"action": "update",
    "toggle": false,
	  "led-count": 100,
  	"brightness": 50,
	  "color": {
      "red": 125,
      "green": 54,
      "blue": 34
    }
  }
  """
  log(request.full_path, debug=True)
  for path_var in path_vars:
    log(f"  path variable = '{path_var}': '{path_vars[path_var]}'")
    if path_var == "light_name":
      light_name=path_vars[path_var]
  for arg in request.args:
    log(f"  argument     = '{arg}': '{request.args[arg]}'")
  # We're going to assume that we receive a JSON data payload if we receive anything.
  # We just ignore everything if it's not JSON.
  if request.is_json:
    log("JSON payload:")
    log(request.json)
  # We're also very flexible in the payload structure!  We try to parse some fields and don't care too much
  # if we don't find values in the spots that we expect them.
  # If we don't find any usefull data, then we just toggle the ledstrip on or off.
  _action=request.json.get("action")
  _toggle=request.json.get("toggle")
  _brightness=request.json.get("brightness")
  _redRGB=request.json.get("color").get("red")
  _greenRGB=request.json.get("color").get("green")
  _blueRGB=request.json.get("color").get("blue")
  _ledCount=request.json.get("led-count")
  _returnValue={}
  # Remove leading or trailing slashes and questionmarks.
  # In real life, this is removing the leading slash and trailing questionmark
  _self=request.host_url+request.full_path.strip("/").strip("?")
  _returnValue["self"]=_self
  # Go find the light:
  _found=False
  for light in lights:
    if light.name == light_name:
      _found=True
      break
  if _found:
    # We found the light.  Generate the payload to send back with the light's details:
    light.ledCount=_ledCount
    light.ledBrightness=_brightness
    light.redRGB=_redRGB
    light.greenRGB=_greenRGB
    light.blueRGB=_blueRGB
#    # Set Christmass mode :-)
#    light.behaviorModeName="Christmass"
    light.behaviorModeName="Default"
    if _toggle:
      # The user requests to toggle the light on or off:
      light.Toggle()
    else:
      # The user changed values and we need to update the leds:
      light.Update()
    html=f"<h1>POST - Updated light {light.name} - {light.state}</h1><br>"
    html+=f"<a href='/light/{light.name}'>{light.name}</a>"
  else:
    # We can't find this light!  Oops...
    _errors=[]
    _errors.append({"error": f"Light '{light_name}' not found!"})
    _returnValue["errors"]=_errors
  return json.dumps(_returnValue)


#def apiGETLightSwitches(host_url, uri, path_vars, parms) -> str:
def apiGETLightSwitches(path_vars, request) -> str:
  """ Callback function for the GET operation at the '/light/<light_name>/switches' endpoint. """
  log(request.full_path, debug=True)
  for path_var in path_vars:
    log(f"  path variable = '{path_var}': '{path_vars[path_var]}'")
    if path_var == "light_name":
      light_name=path_vars[path_var]
  for arg in request.args:
    log(f"  argument     = '{arg}': '{request.args[arg]}'")
  _returnValue={}
  # Remove leading or trailing slashes and questionmarks.
  # In real life, this is removing the leading slash and trailing questionmark
  _self=request.host_url+request.full_path.strip("/").strip("?")
  _returnValue["self"]=_self
  # Go find the light:
  _found=False
  for light in lights:
    if light.name == light_name:
      _found=True
      break
  if _found:
    # We found the light.  Generate the payload to send back with the light's switches:
    html=f"<h1>GET - Light {light.name}, Switches</h1>"
    for switch in light.switches:
      html+=f"<a href='/light/{light.name}/switch/{switch.name}'>{switch.name}</a><br>"
    html+=f"<a href='/light/{light_name}'>Light {light_name}</a><br>"
    html+="<a href='/lights'>Lights</a><br>"
  else:
    # We can't find this light!  Oops...
    _errors=[]
    _errors.append({"error": f"Light {light_name} not found!"})
    _returnValue["errors"]=_errors
  return json.dumps(_returnValue)


#def apiGETLightSwitch(host_url, uri, path_vars, parms) -> str:
def apiGETLightSwitch(path_vars, request) -> str:
  """ Callback function for the GET operation at the '/light/<light_name>/switch/<switch_name>' endpoint. """
  log(request.full_path, debug=True)
  for path_var in path_vars:
    log(f"  path variable = '{path_var}': '{path_vars[path_var]}'")
    if path_var == "light_name":
      light_name=path_vars[path_var]
    elif path_var == "switch_name":
      switch_name=path_vars[path_var]
  for arg in request.args:
    log(f"  argument     = '{arg}': '{request.args[arg]}'")
  _returnValue={}
  # Remove leading or trailing slashes and questionmarks.
  # In real life, this is removing the leading slash and trailing questionmark
  _self=request.host_url+request.full_path.strip("/").strip("?")
  _returnValue["self"]=_self
  # Go find the light:
  _found=False
  for light in lights:
    if light.name == light_name:
      _found=True
      break
  if _found:
    # We found the light.  We now need to find this light's switch:
    _found=False
    for switch in light.switches:
      _found=True
      break
    if _found:
      html=f"<h1>GET - Light {light.name}, switch {switch.state}</h1>"
      html+=f"<a href='/light/{light_name}/switches'>{light_name} switches</a><br>"
      html+=f"<a href='/light/{light_name}'>Light {light_name}</a><br>"
      html+="<a href='/lights'>Lights</a><br>"
    else:
      # We can't find this switch!  Oops...
      html=f"<h1>GET - Light {light_name}, Switch {switch_name} not found!:</h1>"
      html+=f"<a href='/light/{light_name}/switches>Switches</a><br>"
      html+="<a href='/lights'>Lights</a><br>"
  else:
    # We can't find this light!  Oops...
    _errors=[]
    _errors.append({"error": f"Light {light_name} not found!"})
    _returnValue["errors"]=_errors
  return json.dumps(_returnValue)


#--------------------------------------------------#
# The app starts here...
#--------------------------------------------------#
if __name__ == '__main__':
#  log(f"number of threads: {threading.activeCount()}")
  log("Reading the config...")
  apiServer=None        # the REST API server wrapper
  lights=[]             # list of Light objects (typically 1)

  # We run this app as a daemon on the Raspberry PI, which means that we most probably run this from a different
  # directory.  The lights.yaml file is in the same directory as this app, so make sure we explicitly set the
  # directory before trying to open the file:
  _dir=os.path.dirname(__file__)
  if not _dir == "":
    log(f"Running this in directory: {_dir}")
    os.chdir(_dir)

  # Now open the yaml config-file and read it:
  with open("lights.yaml", 'r') as stream:
    try:
      config=yaml.safe_load(stream)
    except yaml.YAMLError as exc:
      log(exc)
      sys.exit(1)

  # There may be config for multiple lights in the yaml-file.
  # Lets set them all up:
  log(f"config: {config}", debug=True)

  # The API server is optional:
  try:
    apiserver_config=config["apiserver"]
    _name=apiserver_config["name"]
    _port=apiserver_config["port"]
    log("API Server:")
    log(f" name: {_name}")
    log(f" port: {_port}")
    apiServer=RESTserver(_name)
    apiServer.debug=DEBUG
    apiServer.port=_port
    del apiserver_config   # No longer need this config in memory
    del _name
    del _port
  except:
    log("there's no config for an API server")

  lights_config=config["lights"]
  log(f"Number of light configurations: {len(lights_config)}", debug=True)
  log("===================")
  for light_config in lights_config:
    log("Light:")
    log(f"light: {light_config}", debug=True)
    _name=light_config['name']
    _ledCount=light_config['led_count']
    _brightness=light_config['brightness']
    _gpioPin=light_config['gpio_pin']
    log(f" name: {_name}")
    log(f" led count: {_ledCount}")
    log(f" brightness: {_brightness}")
    log(f" GPIO pin: {_gpioPin}")
    # Create a light instance and set its properties:
    _light=Light(_name)
    _light.debug=DEBUG
    _light.ledCount=_ledCount
    _light.ledBrightness=_brightness
    _light.stripGpioPin=_gpioPin

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
      log("there are no switches configured for this light")
    else:
      # Lets set them all up for this light:
      for switch_config in switches_config:
        log(" switch:")
        log(f"switch config: {switch_config}", debug=True)
        _name=switch_config['name']
        _gpioPin=switch_config['gpio_pin']
        log(f"  name: {_name}")
        log(f"  GPIO pin: {_gpioPin}")
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
    log("---------------")
    for light in lights:
      log(f"Light object: {light.name}")
      for switch in light.switches:
        log(f"  Switch object: {switch.name}")
    log("---------------")

  log("===================")
  # The API server is optional, so don't try to configure and start one if we don't have one set up:
  if isinstance(apiServer, RESTserver):
    log("Setting up routing rules in the API server...")
    #  allowedMethods=['GET','POST','PUT','DELETE',])

    # View the whole setup: http://0.0.0.0:80/
    log("  setting up: /")
    apiServer.add_endpoint(endpoint='/', \
                           endpoint_name='home', \
                           getHandler=apiGETHome, \
#                           htmlTemplateFile='home.html', \
#                           htmlTemplateData={'title': 'Ledstrip', \
#                                             'name': '<oops>', \
#                                             'switches': '[oops]'}, \
                           allowedMethods=['GET',])
    # View all the Light objects in the setup: http://0.0.0.0:80/lights
    log("  setting up: /lights")
    apiServer.add_endpoint(endpoint='/lights', \
                           endpoint_name='lights', \
                           getHandler=apiGETLights, \
                           allowedMethods=['GET',])
    # View the setup of 1 specific Light object: http://0.0.0.0:80/light/<name>
    # 'GET' shows the config;
    # 'POST' to update its config (config in body as JSON payload);
    log("  setting up: /light/<light_name>")
    apiServer.add_endpoint(endpoint='/light/<light_name>', \
                           endpoint_name='light', \
                           getHandler=apiGETLight, \
                           postHandler=apiPOSTLight, \
                           allowedMethods=['GET','POST',])
    # View all the Switch objects in the setup for a specific Light: http://0.0.0.0:80/light/<name>/switches
    log("  setting up: /light/<light_name>/switches")
    apiServer.add_endpoint(endpoint='/light/<light_name>/switches', \
                           endpoint_name='switches', \
                           getHandler=apiGETLightSwitches, \
                           allowedMethods=['GET',])
    # View the setup of 1 specific Switch object for a specific Light: http://0.0.0.0:80/light/<name>/switch/<name>
    log("  setting up: /light/<light_name>/switch/<switch_name>")
    apiServer.add_endpoint(endpoint='/light/<light_name>/switch/<switch_name>', \
                           endpoint_name='switch', \
                           getHandler=apiGETLightSwitch, \
                           allowedMethods=['GET',])

    log("Starting the REST API server...")
    apiServer.start()

  log('Press Ctrl-C to quit.')

  try:
    while True:
      # Infinite loop, checking each button status every so many milliseconds and toggling the lights
      # if a change in one of the switches is detected:
      sleep(0.5)
      log("checking switches...", debug=True)
      for light in lights:
        for switch in light.switches:
          if switch.hasChanged():
            log(f"switch {switch.name} event -> toggling light {light.name}", debug=True)
            # We want the switch to always turn on the ledstrip with white light and full brightness.
            if light.state:
              # The light is on.  Turn it off without changing settings:
              light.Off()
            else:
              # The light is off.
              # Get the current settings:
              _module=light.behaviorModuleName
              _red=light.redRGB
              _green=light.greenRGB
              _blue=light.blueRGB
              _brightness=light.ledBrightness
              # Change the settings to standard on/off, white with full brightness:
              light.behaviorModuleName="Default"
#              light.behaviorModuleName="Christmass"
              light.redRGB=255
              light.greenRGB=255
              light.blueRGB=255
              light.ledBrightness=255
              # Turn the light on:
              light.On()
              # Restore the settings:
              light.behaviorModuleName=_module
              light.redRGB=_red
              light.greenRGB=_green
              light.blueRGB=_blue
              light.ledBrightness=_brightness

  except KeyboardInterrupt:
    # Ctrl-C was hit!
    log("...ending app...")

  finally:
    # Destroy the objects, invoking their destructors, which will turn off the light and clean up all the resources:
    del apiServer
    for light in lights:
      for switch in light.switches:
        log(f"destroying switch: {switch.name}", debug=True)
        light.delSwitch(switch)
      log(f"destroying light: {light.name}", debug=True)
      del light
    # Release the ports that were setup on the RPi for this app:
    Switch.cleanUp()
    # Then stop the app...
    log("I'm out of here! Adios...\n")