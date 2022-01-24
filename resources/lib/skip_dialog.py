import xbmc
import xbmcgui

from resources.lib import tools

OK_BUTTON = 201
ACTION_PREVIOUS_MENU = 10
ACTION_BACK = 92


class IntroSkipDialog(xbmcgui.WindowXMLDialog):
    def __init__(self, xmlFilename, scriptPath, defaultSkin='Default', defaultRes='720p'):
        self.skip_time = 0

    def set_skip_time(self, skip_time):
        self.skip_time = skip_time

    def onInit(self):
        skipLabel = "SKIP TO {}".format(self.skip_time)
        skipButton = self.getControl(OK_BUTTON)
        skipButton.setLabel(skipLabel)
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU or action == ACTION_BACK:
            self.close()

    def onControl(self, control):
        pass

    def onFocus(self, control):
        pass

    def onClick(self, control):
        if control == OK_BUTTON:
            xbmc.Player().seekTime(tools.convert_time_to_seconds(self.skip_time) - 1)

            self.close()