# ToDo: - create a light class
#       - turn each light into a light instance so we don't duplicate all the code
#       - 

# 20220119 - Kivy and KivyMD seem to have issues running in Python 3.10
#            run: /> python3.9 ledstrips.py

#
# Kivy installation:
#   Make sure to have OpenGL and its headers installed (needed to build the Kivy wheel on your machine).
#     (Fedora 35 package names: libglvnd-opengl, libglvnd-devel)
#     (Kivy installation was failing on my Fedora machine after upgrade to v35, which apparently removed the OpenGL development files)
#   /> pip install kivy
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
kivy.require('2.2.1')

import kivymd
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.behaviors import elevation
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch

# Not implemented yet in KivyMD (v0.104.2)
# Will be implemented in KivyMD v1.0.0
#from kivymd.uix.picker import MDColorPicker
#
# To update:
#   /> pip show kivymd
#        Version: 0.104.2
#   /> pip install kivymd -U
#
#   /> conda list kivymd
#        packages in environment at /home/jcreyf/anaconda3/envs/ledstrips:
#          Name                    Version                   Build  Channel
#          kivymd                    0.104.1            pyhd8ed1ab_0    conda-forge
#   /> conda update kivymd

class LedstripsApp(MDApp):
  _version = "v0.1.9"

  _LunaURL="http://192.168.5.12:8888/light/Luna"
  _LunaStatus=False
  _LunaLedCount=0
  _LunaRed=0
  _LunaGreen=0
  _LunaBlue=0
  _LunaWhite=0
  _LunaBrightness=1

  _bedroomURL="http://192.168.5.10:8888/light/Bedroom"
  _bedroomStatus=False
  _bedroomLedCount=0
  _bedroomRed=0
  _bedroomGreen=0
  _bedroomBlue=0
  _bedroomWhite=0
  _bedroomBrightness=1

  _loftURL="http://192.168.5.11:8888/light/Loft"
  _loftStatus=False
  _loftLedCount=0
  _loftRed=0
  _loftGreen=0
  _loftBlue=0
  _loftWhite=0
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
      _white = int(self.sliderWhite_loft.value)
      _brightness = int(self.sliderBrightness_loft.value)
      if self._loftRed != _red or \
         self._loftGreen != _green or \
         self._loftBlue != _blue or \
         self._loftWhite != _white or \
         self._loftBrightness != _brightness:
           _toggle=False
      else:
        _toggle=True

      if self.chkMode_loft.active:
        _behavior="Christmass"
      else:
        _behavior="Default"

      data={"action": "update",
            "toggle": _toggle,
            "behavior": _behavior,
            "led-count": self._loftLedCount,
            "brightness": _brightness,
            "color": {
              "red": _red,
              "green": _green,
              "blue": _blue,
              "white": _white
            }
      }
#      print(data)
      data=json.dumps(data)
      data=data.encode('utf-8')
      req=urllib.request.Request(self._loftURL, data=data)
      req.add_header("Content-Type", "application/json")
      contents = urllib.request.urlopen(req).read()
      print(contents)
      self.text_log.text = str(contents)
      # Update the locally saved values:
      self._loftRed=_red
      self._loftGreen=_green
      self._loftBlue=_blue
      self._loftWhite=_white
      self._loftBrightness=_brightness
      # Update the switch in the GUI:
      self._loftStatus=not self._loftStatus
      self.switchStatus_loft.active=self._loftStatus
    except Exception as e:
      self.text_log.text = str(e)


  def bedroom(self, args):
    self.text_log.text = ""
    try:
      # Determine if we should toggle the light on/off or simply update its values:
      _red = int(self.sliderRed_bedroom.value)
      _green = int(self.sliderGreen_bedroom.value)
      _blue = int(self.sliderBlue_bedroom.value)
      _white = int(self.sliderWhite_bedroom.value)
      _brightness = int(self.sliderBrightness_bedroom.value)
      if self._bedroomRed != _red or \
         self._bedroomGreen != _green or \
         self._bedroomBlue != _blue or \
         self._bedroomWhite != _white or \
         self._bedroomBrightness != _brightness:
           _toggle=False
      else:
        _toggle=True

      if self.chkMode_bedroom.active:
        _behavior="Christmass"
      else:
        _behavior="Default"

      data={"action": "update",
            "toggle": _toggle,
            "behavior": _behavior,
            "led-count": self._bedroomLedCount,
            "brightness": _brightness,
            "color": {
              "red": _red,
              "green": _green,
              "blue": _blue,
              "white": _white
            }
      }
#      print(data)
      data=json.dumps(data)
      data=data.encode('utf-8')
      req=urllib.request.Request(self._bedroomURL, data=data)
      req.add_header("Content-Type", "application/json")
      contents = urllib.request.urlopen(req).read()
      self.text_log.text = str(contents)
      # Update the locally saved values:
      self._bedroomRed=_red
      self._bedroomGreen=_green
      self._bedroomBlue=_blue
      self._bedroomWhite=_white
      self._bedroomBrightness=_brightness
    except Exception as e:
      self.text_log.text = str(e)


  def Luna(self, args):
    self.text_log.text = ""
    try:
      # Determine if we should toggle the light on/off or simply update its values:
      _red = int(self.sliderRed_Luna.value)
      _green = int(self.sliderGreen_Luna.value)
      _blue = int(self.sliderBlue_Luna.value)
      _white = int(self.sliderWhite_Luna.value)
      _brightness = int(self.sliderBrightness_Luna.value)
      if self._LunaRed != _red or \
         self._LunaGreen != _green or \
         self._LunaBlue != _blue or \
         self._LunaWhite != _white or \
         self._LunaBrightness != _brightness:
           _toggle=False
      else:
        _toggle=True

      if self.chkMode_Luna.active:
        _behavior="Christmass"
      else:
        _behavior="Default"

      data={"action": "update",
            "toggle": _toggle,
            "behavior": _behavior,
            "led-count": self._LunaLedCount,
            "brightness": _brightness,
            "color": {
              "red": _red,
              "green": _green,
              "blue": _blue,
              "white": _white
            }
      }
#      print(data)
      data=json.dumps(data)
      data=data.encode('utf-8')
      req=urllib.request.Request(self._LunaURL, data=data)
      req.add_header("Content-Type", "application/json")
      contents = urllib.request.urlopen(req).read()
      self.text_log.text = str(contents)
      # Update the locally saved values:
      self._LunaRed=_red
      self._LunaGreen=_green
      self._LunaBlue=_blue
      self._LunaWhite=_white
      self._LunaBrightness=_brightness
    except Exception as e:
      self.text_log.text = str(e)


  def build(self):
    screen = MDScreen(
      md_bg_color=MDApp.get_running_app().theme_cls.primary_color
    )
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
      pos_hint = {"center_x": 0.5, "center_y": 0.08},
      halign = "center",
      theme_text_color = "Error"
    )
    screen.add_widget(self.text_log)


    #
    # Button Loft:
    #
    # Get the status of the ledstrip:
    try:
      req=urllib.request.urlopen(self._loftURL)
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
      self._loftWhite=contents["light"]["color"]["white"]
    except Exception as e:
      self.text_log.text = str(e)

    _loft_pos=0.80
    self.switchStatus_loft = MDSwitch(
      active=self._loftStatus,
      pos_hint={"center_x": 0.15, "center_y": _loft_pos},
      size_hint_x=0.10,
      size_hint_y=0.10,
      on_release = self.loft
    )
    screen.add_widget(self.switchStatus_loft)
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
      size_hint_y=0.04
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
      size_hint_y=0.04
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
      size_hint_y=0.04
    )
    screen.add_widget(self.sliderBlue_loft)
    self.sliderWhite_loft = MDSlider(
      min=0,
      max=255,
      value=self._loftWhite,
      color='white',
      hint=True,
      hint_radius=4,
      hint_bg_color='white',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _loft_pos-0.16},
      size_hint_x=0.9,
      size_hint_y=0.04
    )
    screen.add_widget(self.sliderWhite_loft)
    self.sliderBrightness_loft = MDSlider(
      min=1,
      max=255,
      value=self._loftBrightness,
      color='black',
      hint=True,
      hint_radius=4,
      hint_bg_color='black',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _loft_pos-0.19},
      size_hint_x=0.9,
      size_hint_y=0.04
    )
    screen.add_widget(self.sliderBrightness_loft)


    #
    # Button Bedroom:
    #
    # Get the status of the ledstrip:
    try:
      req=urllib.request.urlopen(self._bedroomURL)
      res=req.read()
      contents = json.loads(res.decode("utf-8"))
#      self.text_log.text = str(contents)
      self._bedroomStatus=contents["light"]["state"]
      self._bedroomLedCount=contents["light"]["led-count"]
      self._bedroomBrightness=contents["light"]["brightness"]
      self._bedroomRed=contents["light"]["color"]["red"]
      self._bedroomGreen=contents["light"]["color"]["green"]
      self._bedroomBlue=contents["light"]["color"]["blue"]
      self._bedroomBlue=contents["light"]["color"]["white"]
    except Exception as e:
      self.text_log.text = str(e)

    _bedroom_pos=0.55
    self.switchStatus_bedroom = MDSwitch(
      active=self._bedroomStatus,
      pos_hint={"center_x": 0.15, "center_y": _bedroom_pos},
      size_hint_x=0.10,
      size_hint_y=0.10,
      on_release = self.bedroom
    )
    screen.add_widget(self.switchStatus_bedroom)
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
      size_hint_y=0.04
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
      size_hint_y=0.04
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
      size_hint_y=0.04
    )
    screen.add_widget(self.sliderBlue_bedroom)
    self.sliderWhite_bedroom = MDSlider(
      min=0,
      max=255,
      value=self._bedroomWhite,
      color='white',
      hint=True,
      hint_radius=4,
      hint_bg_color='white',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _bedroom_pos-0.16},
      size_hint_x=0.9,
      size_hint_y=0.04
    )
    screen.add_widget(self.sliderWhite_bedroom)
    self.sliderBrightness_bedroom = MDSlider(
      min=1,
      max=255,
      value=self._bedroomBrightness,
      color='black',
      hint=True,
      hint_radius=4,
      hint_bg_color='black',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _bedroom_pos-0.19},
      size_hint_x=0.9,
      size_hint_y=0.04
    )
    screen.add_widget(self.sliderBrightness_bedroom)


    #
    # Button Luna:
    #
    # Get the status of the ledstrip:
    # {
    #    "self": "http://192.168.5.12:8888/light/Luna",
    #    "light": {
    #      "name": "Luna",
    #      "uri": "http://192.168.5.12:8888/light/Luna",
    #      "state": false,
    #      "led-count": 140,
    #      "color": {
    #        "red": 1,
    #        "green": 1,
    #        "blue": 1,
    #        "white": 1
    #      },
    #      "brightness": 255
    #    },
    #    "switches": [
    #      {
    #        "name": "Desk",
    #        "uri": "http://192.168.5.12:8888/light/Luna/switch/Desk",
    #        "state": 1
    #      }
    #    ]
    #  }
    try:
      req=urllib.request.urlopen(self._LunaURL)
      res=req.read()
      contents = json.loads(res.decode("utf-8"))
#      self.text_log.text = str(contents)
      self._LunaStatus=contents["light"]["state"]
      self._LunaLedCount=contents["light"]["led-count"]
      self._LunaBrightness=contents["light"]["brightness"]
      self._LunaRed=contents["light"]["color"]["red"]
      self._LunaGreen=contents["light"]["color"]["green"]
      self._LunaBlue=contents["light"]["color"]["blue"]
      self._LunaBlue=contents["light"]["color"]["white"]
    except Exception as e:
      self.text_log.text = str(e)

    _Luna_pos=0.30
    self.switchStatus_Luna = MDSwitch(
      active=self._LunaStatus,
      pos_hint={"center_x": 0.15, "center_y": _Luna_pos},
      size_hint_x=0.10,
      size_hint_y=0.10,
      on_release = self.Luna
    )
    screen.add_widget(self.switchStatus_Luna)
    screen.add_widget(MDFillRoundFlatButton(
      text="Luna",
      font_size = 24,
      pos_hint = {"center_x": 0.5, "center_y": _Luna_pos},
      on_press = self.Luna
    ))
    self.chkMode_Luna = MDCheckbox(
      active=False,
      pos_hint={"center_x": 0.80, "center_y": _Luna_pos},
      size_hint_x=0.10,
      size_hint_y=0.10
    )
    screen.add_widget(self.chkMode_Luna)
    self.sliderRed_Luna = MDSlider(
      min=0,
      max=255,
      value=self._LunaRed,
      color='red',
      hint=True,
      hint_radius=4,
      hint_bg_color='red',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _Luna_pos-0.07},
      size_hint_x=0.9,
      size_hint_y=0.04
    )
    screen.add_widget(self.sliderRed_Luna)
    self.sliderGreen_Luna = MDSlider(
      min=0,
      max=255,
      value=self._LunaGreen,
      color='green',
      hint=True,
      hint_radius=4,
      hint_bg_color='green',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _Luna_pos-0.10},
      size_hint_x=0.9,
      size_hint_y=0.04
    )
    screen.add_widget(self.sliderGreen_Luna)
    self.sliderBlue_Luna = MDSlider(
      min=0,
      max=255,
      value=self._LunaBlue,
      color='blue',
      hint=True,
      hint_radius=4,
      hint_bg_color='blue',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _Luna_pos-0.13},
      size_hint_x=0.9,
      size_hint_y=0.04
    )
    screen.add_widget(self.sliderBlue_Luna)
    self.sliderWhite_Luna = MDSlider(
      min=0,
      max=255,
      value=self._LunaWhite,
      color='white',
      hint=True,
      hint_radius=4,
      hint_bg_color='white',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _Luna_pos-0.16},
      size_hint_x=0.9,
      size_hint_y=0.04
    )
    screen.add_widget(self.sliderWhite_Luna)
    self.sliderBrightness_Luna = MDSlider(
      min=1,
      max=255,
      value=self._LunaBrightness,
      color='black',
      hint=True,
      hint_radius=4,
      hint_bg_color='black',
      hint_text_color='black',
      pos_hint = {"center_x": 0.5, "center_y": _Luna_pos-0.19},
      size_hint_x=0.9,
      size_hint_y=0.04
    )
    screen.add_widget(self.sliderBrightness_Luna)


    # Setting it in stone:
    return screen


if __name__ == '__main__':
  LedstripsApp().run()
