from flask import Flask, Response
import threading

# Flask API and config keys:
#   https://flask.palletsprojects.com/en/1.1.x/api/
#   https://flask.palletsprojects.com/en/1.1.x/config/

class RESTserver:
  """
  Class to make the Light objects accessible through web based RESTful services.
  """
  def __init__(self, name):
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
  def debug(self):
    """ Return the debug-state ... True or False (default). """
    return self._debug
  
  @debug.setter
  def debug(self, flag):
    """ Set the debug flag. """
    self._debug=flag

  @property
  def name(self):
    """ Return the name of this RESTful web server. """
    return self._name

  @property
  def port(self):
    """ Return the port number of this RESTful web server. """
    return self._serverPort

  @port.setter
  def port(self, value):
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
    _serverThread.start()



class RESTEndpointAction():
  """
  Class to handle REST API endpoints.
  """
  def __init__(self, action):
    self.action = action

  def __call__(self, *args):
    html = self.action()
    self.response = Response(html, status=200, headers={})
    return self.response
