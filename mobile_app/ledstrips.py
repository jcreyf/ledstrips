#
# KivyMD docs:
#   https://kivymd.readthedocs.io/en/latest/
# Install the KivyMD libraries:
#   /> pip install kivyMD
# To compile into an Android app:
#   https://kivy.org/doc/stable/guide/packaging-android.html
#
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
import urllib.request

class LedstripsApp(MDApp):
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
      contents = urllib.request.urlopen("http://192.168.1.12:8888/light").read()
      self.text_log.text = str(contents)
    except Exception as e:
#      print("Oops!", e, "occurred.")
      self.text_log.text = str(e)

  def build(self):
    screen = MDScreen()
    # Top toolbar:
    self.toolbar = MDToolbar(title="Ledstrips")
    self.toolbar.pos_hint = {"top": 1}
    self.toolbar.right_action_items = [
      # Icon list: https://materialdesignicons.com/
      ["exit-to-app", lambda x: self.exit()]
    ]
    screen.add_widget(self.toolbar)
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
