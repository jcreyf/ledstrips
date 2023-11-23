import urllib.request
import asyncio
import json
import flet
from flet import (
    Column,
    Container,
    Page,
    Row,
    Text,
    UserControl,
    border_radius,
    colors,
)
# https://pypi.org/project/flet-contrib/
# https://github.com/flet-dev/flet-contrib/blob/main/flet_contrib/color_picker/README.md
# https://github.com/flet-dev/flet-contrib/blob/main/flet_contrib/color_picker/src/color_picker.py
from flet_contrib.color_picker import ColorPicker
from typing import List


#---------------------------


class App():
    def __init__(self):
        self._ledstrips: List[LedStrip] = list()

    def addStrip(self):
#        self._ledstrips.append(LedStrip(name="Luna", endpoint="http://192.168.5.12:8888/light/Luna"))
#        self._ledstrips.append(LedStrip(name="Bedroom", endpoint="http://192.168.5.10:8888/light/Bedroom"))
        self._ledstrips.append(LedStrip(name="Loft", endpoint="http://192.168.5.11:8888/light/Loft"))

    def list(self):
        for strip in self._ledstrips:
            print(strip)

    def GUI(self, page: Page):
        page.title="Ledstrips"
        page.window_width=450
        page.window_height=600
        page.scroll="auto"
        page.fonts = {
            "Roboto Mono": "RobotoMono-VariableFont_wght.ttf",
        }
        ledstripsGUI=LedstripsGUI()
        ledstripsGUI.setPage(page)  # Needed for the Markdown control to open hyperlinks
        ledstripsGUI.setLedstrip(self._ledstrips[0])
        page.add(ledstripsGUI)


#---------------------------


class LedStrip():
    _Name: str = ""
    _API_endpoint: str = ""
    _Status: bool = False
    _LedCount: int = 0
    _RedValue: int = 0
    _GreenValue: int = 0
    _BlueValue: int = 0
    _WhiteValue: int = 0
    _BrightnessValue: int = 1
    _MetaData = None
    def __init__(self, name: str, endpoint: str):
        self._Name=name
        self._API_endpoint=endpoint
        asyncio.run(self.getMetadata())

    def __str__(self) -> str:
        return f"Name: {self._Name} (led_count:{self._LedCount}, status:{self._Status})"

    async def getMetadata(self):
        # Get the status of the ledstrip:
        try:
            req=urllib.request.urlopen(self._API_endpoint)
            res=req.read()
            self._MetaData = json.loads(res.decode("utf-8"))
            print(str(self._MetaData))
            self._Status=self._MetaData["light"]["state"]
            self._LedCount=self._MetaData["light"]["led-count"]
            self._BrightnessValue=self._MetaData["light"]["brightness"]
            self._RedValue=self._MetaData["light"]["color"]["red"]
            self._GreenValue=self._MetaData["light"]["color"]["green"]
            self._BlueValue=self._MetaData["light"]["color"]["blue"]
            self._WhiteValue=self._MetaData["light"]["color"]["white"]
        except Exception as e:
            print(str(e))

    def _sendData(self, toggle: bool):
        _behavior = "Default"   # "Default" or "Christmass"
        try:
            data={"action": "update",
                "toggle": toggle,
                "behavior": _behavior,
                "led-count": self._LedCount,
                "brightness": self._BrightnessValue,
                "color": {
                    "red": self._RedValue,
                    "green": self._GreenValue,
                    "blue": self._BlueValue,
                    "white": self._WhiteValue
                }
            }
            data=json.dumps(data)
            data=data.encode('utf-8')
            req=urllib.request.Request(self._API_endpoint, data=data)
            req.add_header("Content-Type", "application/json")
            contents = urllib.request.urlopen(req).read()
            print(str(contents))
        except Exception as e:
            print(str(e))

    def toggle(self):
        self._sendData(toggle=True)

    def setColor(self, red: int = 0, green: int = 0, blue: int = 0):
        self._RedValue = red
        self._GreenValue = green
        self._BlueValue = blue
        self._sendData(toggle=False)

    def setBrightness(self, value: int):
        self._BrightnessValue = value
        self._sendData(toggle=False)

    def getColorHEX(self):
        return "#{:02x}{:02x}{:02x}".format(self._RedValue, 
                                            self._GreenValue, 
                                            self._BlueValue)

    def setColorHEX(self, hex: str):
        rgb = []
        for i in (0, 2, 4):
            decimal = int(hex[i:i+2], 16)
            rgb.append(decimal)
        self.setColor(red=rgb[0], green=rgb[1], blue=rgb[2])

    def toggle(self):
        self._sendData(toggle=True)


#---------------------------


class LedstripsGUI(UserControl):
    def setPage(self, page: flet.Page):
        # Reference to the app's page:
        self._page = page

    def setLedstrip(self, ledstrip: LedStrip):
        self._ledstrip=ledstrip

    def build(self):
        ledstripContainer = LedstripContainer(ledstrip=self._ledstrip,
                                              page=self._page)
        return ledstripContainer


#---------------------------


class LedstripContainer(Container):
    def __init__(self, ledstrip: LedStrip = None, page: flet.Page = None):
        self._ledstrip = ledstrip
        self._page = page
        self.result = Text(value=self._ledstrip.getColorHEX(), color=colors.WHITE, size=20)
        super().__init__(
            width=400,
            bgcolor=colors.BLACK,
            border_radius=border_radius.all(10),
            padding=20,
            content=Column(
                controls=[
                    Row(controls=[self.result], alignment="end"),
                    Row(controls=[self.ColorPickerWidget()],),
                    Row(controls=[self.Payload()])
                ],
            )
        )

    def GenerateContainer(self):
        self.width=400
        self.bgcolor=colors.BLACK
        self.border_radius=border_radius.all(10)
        self.padding=20
        self.content=Column(
            controls=[
                Row(controls=[self.result], alignment="end"),
                Row(controls=[self.ColorPickerWidget()],),
                Row(controls=[self.Payload()])
#                Row(controls=[flet.TextField(label="Ledstrip info:",
#                                            read_only=True,
#                                            multiline=True,
#                                            text_style=flet.TextStyle(font_family="Monospace",
#                                                                        size=9),
#                                            value=json.dumps(self._ledstrip._MetaData, indent=2))])
            ],
        )

    def Payload(self):
        return flet.Markdown(value=f"```json\n{json.dumps(self._ledstrip._MetaData, indent=2)}\n```\nhttp://google.com",
                            extension_set=flet.MarkdownExtensionSet.GITHUB_WEB,
                            selectable=True,
                            # Find a list of themes here:
                            #   https://flet.dev/docs/controls/markdown
                            code_theme="androidstudio",
                            code_style=flet.TextStyle(font_family="Roboto Mono",
                                                        size=12),
#                            auto_follow_links=True,
#                            auto_follow_links_target="_blank",
                            on_tap_link=lambda e: self._page.launch_url(url=e.data)
                            )

    def ColorPickerWidget(self):
        color_picker = ColorPicker(color=self._ledstrip.getColorHEX())

        def select_color(e):
            self.result.value=color_picker.color
            self.result.update()
            # Remove the pound sign ("#") from the color and feed it to the ledstrip:
            self._ledstrip.setColorHEX(color_picker.color[1:])

        def toggle(e):
            self._ledstrip.toggle()
            self._ledstrip.getMetadata()
            self.GenerateContainer()
            self._page.update()

        return flet.Column(
            [
                color_picker,
                flet.FilledButton(text="Select", on_click=select_color),
                flet.FilledButton(text="Toggle", on_click=toggle),
            ]
        )


#---------------------------


if __name__ == '__main__':
    app = App()
    app.addStrip()
    app.list()
    flet.app(target=app.GUI,
             assets_dir="assets")
