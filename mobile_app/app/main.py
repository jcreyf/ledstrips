#
# THIS FILE IS AN EXACT COPY OF ledstrips.py!!!!
# THIS FILE IS REQUIRED FOR BUILDOZER TO GENERATE THE ANDROID APP
#
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
import urllib.request
import json

import kivy
kivy.require('2.0.0')

import kivymd
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.behaviors import elevation
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider

# Not implemented yet in KivyMD (v0.104.2)
# Will be implemented in KivyMD v1.0.0
#from kivymd.uix.picker import MDColorPicker


class LedstripsApp(MDApp):
  _version = "v0.1.4"
  _bureauStatus=False
  _bureauRed=0
  _bureauGreen=0
  _bureauBlue=0
  _bureauBrightness=0

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
    try:
      contents = urllib.request.urlopen("http://192.168.1.10:8888/light").read()
      self.text_log.text = str(contents)
    except Exception as e:
      self.text_log.text = str(e)

  def bureau(self, args):
    self.text_log.text = ""
    try:
      # Determine if we should toggle the light on/off or simply update its values:
      _red = int(self.sliderRed.value)
      _green = int(self.sliderGreen.value)
      _blue = int(self.sliderBlue.value)
      _brightness = int(self.sliderBrightness.value)
      if self._bureauRed != _red or \
         self._bureauGreen != _green or \
         self._bureauBlue != _blue or \
         self._bureauBrightness != _brightness:
           _toggle=False
      else:
        _toggle=True

      url="http://192.168.1.12:8888/light/Bureau"
      data={"action": "update",
            "toggle": _toggle,
            "led-count": 100,
            "brightness": _brightness,
            "color": {
              "red": _red,
              "green": _green,
              "blue": _blue
            }
      }
#      print(data)
      data=json.dumps(data)
      data=data.encode('utf-8')
      req=urllib.request.Request(url, data=data)
      req.add_header("Content-Type", "application/json")
      contents = urllib.request.urlopen(req).read()
      self.text_log.text = str(contents)
      # Update the locally saved values:
      self._bureauRed=_red
      self._bureauGreen=_green
      self._bureauBlue=_blue
      self._bureauBrightness=_brightness
    except Exception as e:
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
      pos_hint = {"center_x": 0.5, "center_y": 0.10},
      halign = "center",
      theme_text_color = "Error"
    )
    screen.add_widget(self.text_log)
    #
    # Button Loft:
    #
    screen.add_widget(MDFillRoundFlatButton(
      text="Loft",
      font_size = 24,
      pos_hint = {"center_x": 0.5, "center_y": 0.80},
      on_press = self.loft
    ))
    #
    # Button Bedroom:
    #
    screen.add_widget(MDFillRoundFlatButton(
      text="Bedroom",
      font_size = 24,
      pos_hint = {"center_x": 0.5, "center_y": 0.60},
      on_press = self.bedroom
    ))
    #
    # Button Bureau:
    #
    # Get the status of the ledstrip:
    # {
    #    "self": "http://192.168.1.12:8888/light/Bureau",
    #    "light": {
    #      "name": "Bureau",
    #      "uri": "http://192.168.1.12:8888/light/Bureau",
    #      "state": false,
    #      "color": {
    #        "red": 1,
    #        "green": 1,
    #        "blue": 1
    #      },
    #      "brightness": 255
    #    },
    #    "switches": [
    #      {
    #        "name": "Desk",
    #        "uri": "http://192.168.1.12:8888/light/Bureau/switch/Desk",
    #        "state": 1
    #      }
    #    ]
    #  }
    try:
      req=urllib.request.urlopen("http://192.168.1.12:8888/light/Bureau")
      res=req.read()
      contents = json.loads(res.decode("utf-8"))
#      self.text_log.text = str(contents)
      self._bureauStatus=contents["light"]["state"]
      self._bureauBrightness=contents["light"]["brightness"]
      self._bureauRed=contents["light"]["color"]["red"]
      self._bureauGreen=contents["light"]["color"]["green"]
      self._bureauBlue=contents["light"]["color"]["blue"]
    except Exception as e:
      self.text_log.text = str(e)

    screen.add_widget(MDFillRoundFlatButton(
      text="Bureau",
      font_size = 24,
      pos_hint = {"center_x": 0.5, "center_y": 0.40},
      on_press = self.bureau
    ))
    self.sliderRed = MDSlider(
      min=0,
      max=255,
      value=self._bureauRed,
      color='red',
      hint=True,
      hint_radius=4,
      hint_bg_color='red',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": 0.30},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderRed)
    self.sliderGreen = MDSlider(
      min=0,
      max=255,
      value=self._bureauGreen,
      color='green',
      hint=True,
      hint_radius=4,
      hint_bg_color='green',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": 0.25},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderGreen)
    self.sliderBlue = MDSlider(
      min=0,
      max=255,
      value=self._bureauBlue,
      color='blue',
      hint=True,
      hint_radius=4,
      hint_bg_color='blue',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": 0.20},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderBlue)
    self.sliderBrightness = MDSlider(
      min=1,
      max=255,
      value=self._bureauBrightness,
      color='black',
      hint=True,
      hint_radius=4,
      hint_bg_color='black',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": 0.15},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderBrightness)
    # Setting it in stone:
    return screen


if __name__ == '__main__':
  LedstripsApp().run()
