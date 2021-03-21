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
    self._hasEndpoints=False

  def __del__(self):
    """ Destructor will turn off the web server. """
    print("destroying API server: "+self._name)
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

  def add_endpoint(self, endpoint=None, endpoint_name=None, allowedMethods=None, \
                   getHandler=None, postHandler=None, htmlTemplateFile=None, htmlTemplateData=None):
    """ Add a url endpoint handler to the REST server.
    Arguments:
      endpoint: url endpoint (ex: `/`; `/light`);
      endpoint_name: human readable name for the endpoint url (ex: 'home' for '/' endpoint);
      allowedMethods: which HTTP operations are allowed at this endpoint? (GET, PUT, POST, DELETE, ...)
                      This needs to be a tuple of strings.  Ex.: ['GET', 'POST',]
      getHandler: callback function to execute when the endpoint is triggered with the GET operation;
      postHandler: callback function to execute when the endpoint is triggered with the POST operation;
      htmlTemplateFile: optional HTML template file to render at this endpoint;
      htmlTemplateData: optional dictionary of data for the HTML template renderer to use;
    """
    # Initialize the REST server if not done yet:
    if self._server == None:
      self.initialize()
    # Now add the new endpoint:
    self._server.add_url_rule(rule=endpoint, \
                              endpoint=endpoint_name, \
                              view_func=RESTEndpointView.as_view(("api_{}").format(endpoint_name), \
                                                                 getHandler=getHandler, \
                                                                 postHandler=postHandler, \
                                                                 htmlTemplateFile=htmlTemplateFile, \
                                                                 htmlTemplateData=htmlTemplateData, \
                                                                 debug=self._debug), \
                              methods=allowedMethods)
    # Set the flag to indicate that we've set up custom routing rules in the server:
    self._hasEndpoints=True

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

    # It makes no sense to start the server and waste all the resources if we don't have any rules configured:
    if not self._hasEndpoints:
      raise Exception("There are no routing rules configured for this app.  It makes no sense to start the API server!")

    # We could have a closer look the rules (Flask comes with at least 1 static rule out of the box):
#    for rule in self._server.url_map.iter_rules():
#      print(rule)

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

  def __init__(self, getHandler=None, postHandler=None, htmlTemplateFile=None, htmlTemplateData=None, debug=False):
    """ Store the function to execute when the endpoint gets triggered.
    Arguments:
      getHandler: callback function to execute when the GET operation is called (optional);
      postHandler: callback function to execute when the POST operation is called (optional);
      htmlTemplateFile: HTML template file to render (optional);
      htmlTemplateData: data for the template to render (optional);
    """
    self._getHandler=getHandler
    self._postHandler=postHandler
    self._htmlTemplateFile=htmlTemplateFile
    self._htmlTemplateData=htmlTemplateData
    self._debug=debug

  def log(self, path_vars):
    print("BEGIN DEBUG OUTPUT------------------------")
    print(request.full_path)
    print(("-> Request: {}").format(request))
    # print the arguments that we get from Flask.
    # Setting up an endpoint like '/light/<name>' will call this method with 1 argument: ['name': 'Loft']
    # when this url is called: http://0.0.0.0:<port>/light/Loft
    print(("-> Number of path variables in call: {}").format(len(path_vars)))
    for key, value in path_vars.items():
      print(("  path var    -> '{}': '{}'").format(key, value))
    print(("-> Number of arguments in call: {}").format(len(request.args)))
    for arg in request.args:
      print(("  request arg -> '{}': '{}'").format(arg, request.args[arg]))
    if len(request.data) > 0:
      print("-> Body:")
      print(request.data)
    print(("-> Header count: {}").format(len(request.headers)))
    print(request.headers)
    print("END DEBUG OUTPUT---------------------------")

  def get(self, **path_vars):
    """ GET request.  **path_vars is an optional dictionary with key/values from the url """
    if self._debug:
      print("in MyMethodView:GET")
      self.log(path_vars)
    html=None
    if callable(self._getHandler):
      # Execute  the handler function if one was provided:
      html=self._getHandler(request.host_url, request.full_path, path_vars, request.args)
    if not self._htmlTemplateFile is None:
      # Render the Jinja2 template if one was provided:
      #   https://jinja.palletsprojects.com/en/2.11.x/templates/
      html=render_template(self._htmlTemplateFile, **self._htmlTemplateData)
    if html is None:
      html=("<h1>Oops!  Nothing to render to HTML!</h1>")
    # Create a new flask.Response object and return that:
    return Response(html, status=200, headers={})

  def post(self, **path_vars):
    """ POST request.  **path_vars is an optional dictionary with key/values from the url """
    if self._debug:
      print("in MyMethodView:POST")
      self.log(path_vars)
    html=None
    if callable(self._postHandler):
      # Execute  the handler function if one was provided:
      html=self._postHandler(request.full_path, path_vars, request.args)
    if not self._htmlTemplateFile is None:
      # Render the Jinja2 template if one was provided:
      #   https://jinja.palletsprojects.com/en/2.11.x/templates/
      html=render_template(self._htmlTemplateFile, **self._htmlTemplateData)
    if html is None:
      html=("<h1>Oops!  Nothing to render to HTML!</h1>")
    # Create a new flask.Response object and return that:
    return Response(html, status=200, headers={})
