# https://kivymd.readthedocs.io/en/latest/
# Run: pip install kivyMD
#
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDToolbar
import urllib.request

class LedstripsApp(MDApp):
  def exit(self):
    MDApp.get_running_app().stop()

  def loft(self, args):
    print("Loft")
    contents = urllib.request.urlopen("http://192.168.1.11:8888/light").read()
    print(contents)

  def bedroom(self, args):
    print("Bedroom")
    contents = urllib.request.urlopen("http://192.168.1.10:8888/light").read()
    print(contents)

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
    # Setting it in stone:
    return screen


if __name__ == '__main__':
  LedstripsApp().run()
