"""
This module contains the classes for the RESTfull webservices server.
This server is a light weight http(s) server that we use to expose JSON based REST endpoints that can be used
to control processes on the Raspberry PI (for example to turn lights on or off; set LED colors; ...).

Classes in this module:
- 'RESTserver': metadata and controls for a Flask server (running in a separate thread to avoid blocking of the
   main application thread);
- 'RESTEndpointAction': a REST webservice endpoint url and a reference to the code that should get executed at
   that endpoint;

This module requires these modules:
- FLask and Response classes from the flask module;
- threading module;
"""

from flask import Flask, Response
import threading

# Flask API and config keys:
#   https://flask.palletsprojects.com/en/1.1.x/api/
#   https://flask.palletsprojects.com/en/1.1.x/config/

class RESTserver:
  """
  Class to make the Light objects accessible through RESTful web services.

  The web server is run in a separate thread to avoid it from blocking the main application thread.
  """

  def __init__(self, name: str):
    """ Basic constructor for a new Light REST web server. """
    print("creating REST server: "+name)
    self._name=name
    self._debug=False
    self._serverPort=None
    self._server=None
    self._serverThread=None

  def __del__(self):
    """ Destructor will turn off the web server. """
    print("destroying REST server: "+self._name)
    if not self._server == None:
      self._server.shutdown()
      del self._server

  @property
  def debug(self) -> bool:
    """ Return the debug-state ... True or False (default). """
    return self._debug
  
  @debug.setter
  def debug(self, flag: bool):
    """ Set the debug flag. """
    self._debug=flag

  @property
  def name(self) -> str:
    """ Return the name of this RESTful web server. """
    return self._name

  @property
  def port(self) -> int:
    """ Return the port number of this RESTful web server. """
    return self._serverPort

  @port.setter
  def port(self, value: int):
    """ Set the port of this RESTful web server.  This is an integer between 1 and 65535. """
    if value < 1 or value > 65535: raise Exception("The server port should be between 1 and 65535!")
    self._serverPort=value
  
  def initialize(self):
    """ Initialize the RESTful web server and set the /light end point. """
    print(("initializing REST server {} on port {}").format(self._name, self._serverPort))
    self._server=Flask(self._name)

  def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
    """ Add a url endpoint handler to the REST server. """
    # Initialize the REST server if not done yet:
    if self._server == None:
      self.initialize()
    # Now add the new endpoint:
    self._server.add_url_rule(endpoint, endpoint_name, RESTEndpointAction(handler))

  def start(self):
    """ 
    Start the RESTful API web server.
    The server is started in a separate thread to avoid it blocking the operation of the switches.
    """
    print("Starting REST server: "+self._name)
    # Do some validation before trying to start the server:
    if self._serverPort == None: raise Exception("Can't start the REST API server!  Need to set the network port!")
    # Initialize the REST server if not done yet:
    if self._server == None:
      self.initialize()
    # Turns out that Flask throws an exception when DEBUG is enabled when the server runs in a separate thread!
    # Also need to disable the reloader.
    #   "ValueError: signal only works in main thread"
    self._server.config.update(DEBUG=False, \
                               USE_RELOADER=False, \
                               APPLICATION_ROOT='/')
    _serverThread=threading.Thread(name=("{}_API").format(self._name), \
                                   target=self._server.run, \
                                   kwargs={'host': '0.0.0.0', 'port': self._serverPort})
    _serverThread.setDaemon(True)
    _serverThread.start()

#
#------------------------------------
#

class RESTEndpointAction():
  """
  Class to handle a single RESTfull API endpoint.
  Each API endpoint is wrapped in a RESTEndpointAction object, which is then attached to the web server
  through the '<RESTServer>.add_endpoint(handler=<object>)' method.
  """
  def __init__(self, action):
    """ Store the function to execute when the endpoint gets triggered. """
    self.action = action

  def __call__(self, *args):
    """ Execute the stored function each time the endpoint gets triggered. """
    html = self.action()
    self.response = Response(html, status=200, headers={})
    return self.response
