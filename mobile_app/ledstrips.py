# ToDo: - create a light class
#       - turn each light into a light instance so we don't duplicate all the code
#       - 

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
from kivymd.uix.selectioncontrol import MDCheckbox

# Not implemented yet in KivyMD (v0.104.2)
# Will be implemented in KivyMD v1.0.0
#from kivymd.uix.picker import MDColorPicker


class LedstripsApp(MDApp):
  _version = "v0.1.6"
  _bureauStatus=False
  _bureauLedCount=0
  _bureauRed=0
  _bureauGreen=0
  _bureauBlue=0
  _bureauBrightness=1

  _bedroomStatus=False
  _bedroomLedCount=0
  _bedroomRed=0
  _bedroomGreen=0
  _bedroomBlue=0
  _bedroomBrightness=1

  _loftStatus=False
  _loftLedCount=0
  _loftRed=0
  _loftGreen=0
  _loftBlue=0
  _loftBrightness=1

  def exit(self):
    MDApp.get_running_app().stop()


  def loft(self, args):
    self.text_log.text = ""
    try:
      # Determine if we should toggle the light on/off or simply update its values:
      _red = int(self.sliderRed_loft.value)
      _green = int(self.sliderGreen_loft.value)
      _blue = int(self.sliderBlue_loft.value)
      _brightness = int(self.sliderBrightness_loft.value)
      if self._loftRed != _red or \
         self._loftGreen != _green or \
         self._loftBlue != _blue or \
         self._loftBrightness != _brightness:
           _toggle=False
      else:
        _toggle=True

      if self.chkMode_loft:
        _behavior="Christmass"
      else:
        _behavior="Default"

      url="http://192.168.1.11:8888/light/Loft"
      data={"action": "update",
            "toggle": _toggle,
            "behavior": _behavior,
            "led-count": self._loftLedCount,
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
      self._loftRed=_red
      self._loftGreen=_green
      self._loftBlue=_blue
      self._loftBrightness=_brightness
    except Exception as e:
      self.text_log.text = str(e)


  def bedroom(self, args):
    self.text_log.text = ""
    try:
      # Determine if we should toggle the light on/off or simply update its values:
      _red = int(self.sliderRed_bedroom.value)
      _green = int(self.sliderGreen_bedroom.value)
      _blue = int(self.sliderBlue_bedroom.value)
      _brightness = int(self.sliderBrightness_bedroom.value)
      if self._bedroomRed != _red or \
         self._bedroomGreen != _green or \
         self._bedroomBlue != _blue or \
         self._bedroomBrightness != _brightness:
           _toggle=False
      else:
        _toggle=True

      if self.chkMode_bedroom:
        _behavior="Christmass"
      else:
        _behavior="Default"

      url="http://192.168.1.10:8888/light/Bedroom"
      data={"action": "update",
            "toggle": _toggle,
            "behavior": _behavior,
            "led-count": self._bedroomLedCount,
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
      self._bedroomRed=_red
      self._bedroomGreen=_green
      self._bedroomBlue=_blue
      self._bedroomBrightness=_brightness
    except Exception as e:
      self.text_log.text = str(e)


  def bureau(self, args):
    self.text_log.text = ""
    try:
      # Determine if we should toggle the light on/off or simply update its values:
      _red = int(self.sliderRed_bureau.value)
      _green = int(self.sliderGreen_bureau.value)
      _blue = int(self.sliderBlue_bureau.value)
      _brightness = int(self.sliderBrightness_bureau.value)
      if self._bureauRed != _red or \
         self._bureauGreen != _green or \
         self._bureauBlue != _blue or \
         self._bureauBrightness != _brightness:
           _toggle=False
      else:
        _toggle=True

      if self.chkMode_bureau:
        _behavior="Christmass"
      else:
        _behavior="Default"

      url="http://192.168.1.12:8888/light/Bureau"
      data={"action": "update",
            "toggle": _toggle,
            "behavior": _behavior,
            "led-count": self._bureauLedCount,
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
    # Get the status of the ledstrip:
    try:
      req=urllib.request.urlopen("http://192.168.1.11:8888/light/Loft")
      res=req.read()
      contents = json.loads(res.decode("utf-8"))
#      self.text_log.text = str(contents)
      print(contents)
      self._loftStatus=contents["light"]["state"]
      self._loftLedCount=contents["light"]["led-count"]
      self._loftBrightness=contents["light"]["brightness"]
      self._loftRed=contents["light"]["color"]["red"]
      self._loftGreen=contents["light"]["color"]["green"]
      self._loftBlue=contents["light"]["color"]["blue"]
    except Exception as e:
      self.text_log.text = str(e)

    _loft_pos=0.80
    screen.add_widget(MDFillRoundFlatButton(
      text="Loft",
      font_size = 24,
      pos_hint = {"center_x": 0.5, "center_y": _loft_pos},
      on_press = self.loft
    ))
    self.chkMode_loft = MDCheckbox(
      active=False,
      pos_hint={"center_x": 0.80, "center_y": _loft_pos},
      size_hint_x=0.10,
      size_hint_y=0.10
    )
    screen.add_widget(self.chkMode_loft)
    self.sliderRed_loft = MDSlider(
      min=0,
      max=255,
      value=self._loftRed,
      color='red',
      hint=True,
      hint_radius=4,
      hint_bg_color='red',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _loft_pos-0.07},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderRed_loft)
    self.sliderGreen_loft = MDSlider(
      min=0,
      max=255,
      value=self._loftGreen,
      color='green',
      hint=True,
      hint_radius=4,
      hint_bg_color='green',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _loft_pos-0.10},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderGreen_loft)
    self.sliderBlue_loft = MDSlider(
      min=0,
      max=255,
      value=self._loftBlue,
      color='blue',
      hint=True,
      hint_radius=4,
      hint_bg_color='blue',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _loft_pos-0.13},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderBlue_loft)
    self.sliderBrightness_loft = MDSlider(
      min=1,
      max=255,
      value=self._loftBrightness,
      color='black',
      hint=True,
      hint_radius=4,
      hint_bg_color='black',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _loft_pos-0.16},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderBrightness_loft)


    #
    # Button Bedroom:
    #
    # Get the status of the ledstrip:
    try:
      req=urllib.request.urlopen("http://192.168.1.10:8888/light/Bedroom")
      res=req.read()
      contents = json.loads(res.decode("utf-8"))
#      self.text_log.text = str(contents)
      self._bedroomStatus=contents["light"]["state"]
      self._bedroomLedCount=contents["light"]["led-count"]
      self._bedroomBrightness=contents["light"]["brightness"]
      self._bedroomRed=contents["light"]["color"]["red"]
      self._bedroomGreen=contents["light"]["color"]["green"]
      self._bedroomBlue=contents["light"]["color"]["blue"]
    except Exception as e:
      self.text_log.text = str(e)

    _bedroom_pos=0.55
    screen.add_widget(MDFillRoundFlatButton(
      text="Bedroom",
      font_size = 24,
      pos_hint = {"center_x": 0.5, "center_y": _bedroom_pos},
      on_press = self.bedroom
    ))
    self.chkMode_bedroom = MDCheckbox(
      active=False,
      pos_hint={"center_x": 0.80, "center_y": _bedroom_pos},
      size_hint_x=0.10,
      size_hint_y=0.10
    )
    screen.add_widget(self.chkMode_bedroom)
    self.sliderRed_bedroom = MDSlider(
      min=0,
      max=255,
      value=self._bedroomRed,
      color='red',
      hint=True,
      hint_radius=4,
      hint_bg_color='red',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _bedroom_pos-0.07},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderRed_bedroom)
    self.sliderGreen_bedroom = MDSlider(
      min=0,
      max=255,
      value=self._bedroomGreen,
      color='green',
      hint=True,
      hint_radius=4,
      hint_bg_color='green',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _bedroom_pos-0.10},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderGreen_bedroom)
    self.sliderBlue_bedroom = MDSlider(
      min=0,
      max=255,
      value=self._bedroomBlue,
      color='blue',
      hint=True,
      hint_radius=4,
      hint_bg_color='blue',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _bedroom_pos-0.13},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderBlue_bedroom)
    self.sliderBrightness_bedroom = MDSlider(
      min=1,
      max=255,
      value=self._bedroomBrightness,
      color='black',
      hint=True,
      hint_radius=4,
      hint_bg_color='black',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _bedroom_pos-0.16},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderBrightness_bedroom)


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
    #      "led-count": 140,
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
      self._bureauLedCount=contents["light"]["led-count"]
      self._bureauBrightness=contents["light"]["brightness"]
      self._bureauRed=contents["light"]["color"]["red"]
      self._bureauGreen=contents["light"]["color"]["green"]
      self._bureauBlue=contents["light"]["color"]["blue"]
    except Exception as e:
      self.text_log.text = str(e)

    _bureau_pos=0.30
    screen.add_widget(MDFillRoundFlatButton(
      text="Bureau",
      font_size = 24,
      pos_hint = {"center_x": 0.5, "center_y": _bureau_pos},
      on_press = self.bureau
    ))
    self.chkMode_bureau = MDCheckbox(
      active=False,
      pos_hint={"center_x": 0.80, "center_y": _bureau_pos},
      size_hint_x=0.10,
      size_hint_y=0.10
    )
    screen.add_widget(self.chkMode_bureau)
    self.sliderRed_bureau = MDSlider(
      min=0,
      max=255,
      value=self._bureauRed,
      color='red',
      hint=True,
      hint_radius=4,
      hint_bg_color='red',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _bureau_pos-0.07},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderRed_bureau)
    self.sliderGreen_bureau = MDSlider(
      min=0,
      max=255,
      value=self._bureauGreen,
      color='green',
      hint=True,
      hint_radius=4,
      hint_bg_color='green',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _bureau_pos-0.10},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderGreen_bureau)
    self.sliderBlue_bureau = MDSlider(
      min=0,
      max=255,
      value=self._bureauBlue,
      color='blue',
      hint=True,
      hint_radius=4,
      hint_bg_color='blue',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _bureau_pos-0.13},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderBlue_bureau)
    self.sliderBrightness_bureau = MDSlider(
      min=1,
      max=255,
      value=self._bureauBrightness,
      color='black',
      hint=True,
      hint_radius=4,
      hint_bg_color='black',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _bureau_pos-0.16},
      size_hint_x=0.9,
      size_hint_y=0.05
    )
    screen.add_widget(self.sliderBrightness_bureau)


    # Setting it in stone:
    return screen


if __name__ == '__main__':
  LedstripsApp().run()
