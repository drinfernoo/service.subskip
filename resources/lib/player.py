# -*- coding: utf-8 -*-
import xbmc
import xbmcvfs

from resources.lib import settings
from resources.lib import tools
from resources.lib.identify import IdentifyCreditsIntro
from resources.lib.skip_dialog import IntroSkipDialog

_addon_path = xbmcvfs.translatePath(settings.get_addon_info('path'))


class Player(xbmc.Player):
    def __init__(self):
        super().__init__("Player")
        self.dialog = IntroSkipDialog(
            "intro_skip_dialog.xml", _addon_path, "Default", "1080i"
        )

    def reset_intro(self):
        self.dialog.close()
        self.identify.initialize()
        self.intro = None

    def getIntro(self):
        return self.intro

    def onPlayBackStarted(self):
        tools.log("onPlayBackStarted", "debug")
        self.identify = IdentifyCreditsIntro()
        self.intro = None

    def onAVStarted(self):
        tools.log("onAVStarted", "debug")
        if self.getVideoInfoTag().getMediaType() == "episode":
            self.intro = self.identify.get_intro()
            if self.intro:
                tools.log(
                    "Intro detected from {} to {}".format(self.intro[0], self.intro[1]),
                    "info",
                )
            else:
                tools.log("No intro could be detected.", "info")

    def onPlayBackStopped(self):
        tools.log("onPlaybackStopped", "debug")
        self.reset_intro()
        del self.dialog
