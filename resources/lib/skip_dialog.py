import xbmc
import xbmcgui

from resources.lib import settings

OK_BUTTON = 201
ACTION_PREVIOUS_MENU = 10
ACTION_BACK = 92


class IntroSkipDialog(xbmcgui.WindowXMLDialog):
    def __init__(
        self, xmlFilename, scriptPath, defaultSkin='Default', defaultRes='720p'
    ):
        pass

    def onInit(self):
        theme = settings.get_setting("general.theme").lower()
        color = settings.get_setting_string("general.accent_color")

        if theme == "light":
            self.setProperty("theme.color", "fff5f5f5")
        elif theme == "dark":
            self.setProperty("theme.color", "ff232323")

        self.setProperty("theme.accent_color", color)

        self.setProperty("cancelled", "False")

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU or action == ACTION_BACK:
            self.setProperty("cancelled", "True")
            self.close()

    def onClick(self, control):
        if control == OK_BUTTON:
            skip_time = float(self.getProperty("skip_time"))
            xbmc.Player().seekTime(skip_time - 1)
            self.close()

    def isCancelled(self):
        if self.getProperty("cancelled") == "False":
            return False
        elif self.getProperty("cancelled") == "True":
            return True

        return None
