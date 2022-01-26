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
        self.setProperty(
            "button_style",
            "{}_button.png".format(settings.get_setting("general.theme").lower()),
        )

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU or action == ACTION_BACK:
            self.close()

    def onClick(self, control):
        if control == OK_BUTTON:
            skip_time = float(self.getProperty("skip_time"))
            xbmc.Player().seekTime(skip_time - 1)
            self.close()
