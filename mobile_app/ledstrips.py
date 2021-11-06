#
# KivyMD docs:
#   https://kivymd.readthedocs.io/en/latest/
# Install the KivyMD libraries:
#   /> pip install kivyMD
#
# To compile into an Android app:
#   https://kivy.org/doc/stable/guide/packaging-android.html
# For the APK build, make sure to have these installed (in Fedora in my case):
#   https://buildozer.readthedocs.io/en/latest/installation.html#targeting-android
#
import kivy
from kivymd.uix.behaviors import elevation
kivy.require('2.0.0')
import kivymd
import urllib.request
import json

from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
#from kivymd.uix.picker import MDColorPicker

class LedstripsApp(MDApp):
  _version = "v0.1.3"

  def exit(self):
    MDApp.get_running_app().stop()

  def loft(self, args):
    self.text_log.text = ""
    print("Loft")
    try:
      contents = urllib.request.urlopen("http://192.168.1.11:8888/light").read()
      self.text_log.text = str(contents)
    except Exception as e:
#      print("Oops!", e, "occurred.")
      self.text_log.text = str(e)

  def bedroom(self, args):
    self.text_log.text = ""
#    print("Bedroom")
    try:
      contents = urllib.request.urlopen("http://192.168.1.10:8888/light").read()
      self.text_log.text = str(contents)
    except Exception as e:
#      print("Oops!", e, "occurred.")
      self.text_log.text = str(e)

  def bureau(self, args):
    self.text_log.text = ""
#    print("Bureau")
    try:
      url="http://192.168.1.12:8888/light/Bureau"
      data={"action": "toggle",
            "led-count": 100,
            "brightness": 5,
            "color": "0,0,255"
      }
      # Green, Red, Blue
      data=json.dumps(data)
      data=data.encode('utf-8')
      req=urllib.request.Request(url, data=data)
      req.add_header("Content-Type", "application/json")
      contents = urllib.request.urlopen(req).read()
      self.text_log.text = str(contents)
    except Exception as e:
#      print("Oops!", e, "occurred.")
      self.text_log.text = str(e)

  def build(self):
    screen = MDScreen()
    # Top toolbar:
    self.toolbar = MDToolbar(
      title="Ledstrips",
      elevation=20
    )
    self.toolbar.pos_hint = {"top": 1}
    self.toolbar.right_action_items = [
      # Icon list: https://materialdesignicons.com/
      ["exit-to-app", lambda x: self.exit()]
    ]
    screen.add_widget(self.toolbar)
    # Version line:
    screen.add_widget(MDLabel(
      text=self._version,
      font_size = 12,
      pos_hint = {"center_x": 0.5, "center_y": 0.95},
      halign = "center"
    ))
    # Log line:
    self.text_log = MDLabel(
      font_size = 18,
      pos_hint = {"center_x": 0.5, "center_y": 0.20},
      halign = "center",
      theme_text_color = "Error"
    )
    screen.add_widget(self.text_log)
    # Button Loft:
    screen.add_widget(MDFillRoundFlatButton(
      text="Loft",
      font_size = 24,
      pos_hint = {"center_x": 0.5, "center_y": 0.80},
      on_press = self.loft
    ))
    # Button Bedroom:
    screen.add_widget(MDFillRoundFlatButton(
      text="Bedroom",
      font_size = 24,
      pos_hint = {"center_x": 0.5, "center_y": 0.60},
      on_press = self.bedroom
    ))
    # Button Bureau:
    screen.add_widget(MDFillRoundFlatButton(
      text="Bureau",
      font_size = 24,
      pos_hint = {"center_x": 0.5, "center_y": 0.40},
      on_press = self.bureau
    ))
    # Setting it in stone:
    return screen


if __name__ == '__main__':
  LedstripsApp().run()
