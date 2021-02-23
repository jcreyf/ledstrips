"""
This is a mock file to get the app running on a host that doesn't have the
Raspberry PI libraries and modules installed.
"""
class GPIO:
  BCM = None
  IN = None
  PUD_DOWN = None

  def setmode(self):
    pass

  def setup(self, v1, pull_up_down):
    pass

  def cleanup(self):
    pass

  def input(self):
    pass

  def setwarnings(self):
    pass

  def cleanup():
    pass