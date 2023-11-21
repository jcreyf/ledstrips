import kivy
kivy.require('2.1.0')
from kivy.app import App

import sys


class LedstripApp(App):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)


  def btnExit(self):
    sys.exit(0)


if __name__ == '__main__':
  LedstripApp().run()
