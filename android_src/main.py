from kivy.app import App
from kivy.core.window import Window

from ironvale.root import IronvaleRoot


class IronvaleApp(App):
    title = "Ironvale Defense"

    def build(self):
        Window.clearcolor = (0.02, 0.035, 0.03, 1)
        return IronvaleRoot()


if __name__ == "__main__":
    IronvaleApp().run()
