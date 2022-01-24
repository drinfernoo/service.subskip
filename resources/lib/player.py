# -*- coding: utf-8 -*-
import xbmc

from resources.lib import tools
from resources.lib.identify import IdentifyCreditsIntro


class Player(xbmc.Player):
    def __init__(self):
        super().__init__("Player")
        self.identify = IdentifyCreditsIntro()
        self.intro = None

    def reset_intro(self):
        self.identify.initialize()
        self.intro = None

    def onAVStarted(self):
        if self.getVideoInfoTag().getMediaType() == "episode":
        self.intro = identify.get_intro()
        if self.intro:
            tools.log(
                "Intro detected from {} to {}".format(self.intro[0], self.intro[1]),
                "info",
            )
        else:
            tools.log("No intro could be detected.", "info")

    def onPlayBackStopped(self):
        self.reset_intro()
