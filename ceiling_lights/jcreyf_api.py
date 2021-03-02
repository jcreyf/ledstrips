"""
This module contains the classes for the RESTfull webservices server.
This server is a light weight http(s) server that we use to expose JSON based REST endpoints that can be used
to control processes on the Raspberry PI (for example to turn lights on or off; set LED colors; ...).

Classes in this module:
- 'RESTserver': metadata and controls for a Flask server (running in a separate thread to avoid blocking of the
   main application thread);
- 'RESTEndpointView': a REST webservice endpoint url and a reference to the code that should get executed at
   that endpoint;

This module requires these modules:
- FLask and Response classes from the flask module;
- threading module;
"""

from flask import Flask, request, Response, render_template
from flask.views import MethodView
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
# TODO: Need a clean way to stop the server like this:
#       https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c
#      self._server.shutdown()
#      self._serverThread.kill()
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

  def add_endpoint(self, endpoint=None, endpoint_name=None, allowedMethods=None, handler=None, htmlTemplateFile=None, htmlTemplateData=None):
    """ Add a url endpoint handler to the REST server. 
    Arguments:
      endpoint: url endpoint (ex: `/`; `/light`);
      endpoint_name: human readable name for the endpoint url (ex: 'home' for '/' endpoint);
      allowedMethods: which HTTP operations are allowed at this endpoint? (GET, PUT, POST, DELETE, ...)
                      This needs to be a tuple of strings.  Ex.: ['GET', 'POST',]
      handler: callback function to execute when the endpoint is triggered;
      htmlTemplateFile: optional HTML template file to render at this endpoint;
      htmlTemplateData: optional dictionary of data for the HTML template renderer to use;
    """
    # Initialize the REST server if not done yet:
    if self._server == None:
      self.initialize()
    # Now add the new endpoint:
    self._server.add_url_rule(rule=endpoint, \
                              endpoint=endpoint_name, \
                              view_func=RESTEndpointView.as_view('light_api', \
                                                                 handler=handler, \
                                                                 htmlTemplateFile=htmlTemplateFile, \
                                                                 htmlTemplateData=htmlTemplateData), \
                              methods=allowedMethods)
#                             defaults={'light_name': 'testje'})

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

# Look into this:
#   https://pythonise.com/series/learning-flask/flask-api-methodview

class RESTEndpointView(MethodView):
  """
  Class to handle a single RESTfull API endpoint.
  Each API endpoint is wrapped in a RESTEndpointView object, which is then attached to the Flask web server
  through the '<RESTServer>.add_endpoint(handler=<object>)' method.
  """
#  decorators=[validator]

#  def validator(req):
#    def decorator(*args, **kwargs):
#      if not g.user:
#        abort(401)
#      return req(*args, **kwargs)
#    return decorator

  def __init__(self, handler=None, htmlTemplateFile=None, htmlTemplateData=None):
    """ Store the function to execute when the endpoint gets triggered.
    Arguments:
      handler: callback function to execute when object is called;
      htmlTemplateFile: HTML template file to render (optional);
      htmlTemplateData: data for the template to render (optional);
    """
    self._handler=handler
    self._htmlTemplateFile=htmlTemplateFile
    self._htmlTemplateData=htmlTemplateData

  def log(self):
    print("--------------------------------")
    print(request.full_path)
    print(("-> Request: {}").format(request))
    print(("-> Header count: {}").format(len(request.headers)))
    print(request.headers)
    print(("-> Number of arguments in call: {}").format(len(request.args)))
    for arg in request.args:
      print(("  arg = '{}': '{}'").format(arg, request.args[arg]))
    if len(request.data) > 0:
      print("-> Body:")
      print(request.data)

  def get(self, **args):
    """ GET request.  **args is an optional dictionary with key/values from the url """
    print("in MyMethodView:GET")
    self.log()

    # print the arguments that we get from Flask.
    # Setting up an endpoint like '/light/<name>' will call this method with 1 argument: ['name': 'Loft']
    # when this url is called: http://0.0.0.0:<port>/light/Loft
    for key, value in args.items():
      print(("{} -> {}").format(key, value))

    html=None
    if callable(self._handler):
      # Execute  the handler function if one was provided:
      html=self._handler()
    if not self._htmlTemplateFile is None:
      # Render the Jinja2 template if one was provided:
      #   https://jinja.palletsprojects.com/en/2.11.x/templates/
      html=render_template(self._htmlTemplateFile, **self._htmlTemplateData)
    if html is None:
      html=("<h1>Oops!  Nothing to render to HTML!</h1>")
    # Create a new flask.Response object and return that:
    return Response(html, status=200, headers={})

  def post(self, **args):
    # Create
    print("in MyMethodView:POST")
    self.log()
    html=("<h1>POST</h1>")
    # Create a new flask.Response object and return that:
    return Response(html, status=200, headers={})

  def put(self, **args):
    # Update
    print("in MyMethodView:PUT")
    self.log()
    html=("<h1>PUT</h1>")
    # Create a new flask.Response object and return that:
    return Response(html, status=200, headers={})

  def delete(self, **args):
    # Delete
    print("in MyMethodView:DELETE")
    self.log()
    html=("<h1>DELETE</h1>")
    # Create a new flask.Response object and return that:
    return Response(html, status=200, headers={})
