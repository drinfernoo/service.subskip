# -*- coding: utf-8 -*-
import xbmc

from resources.lib import tools
from resources.lib.identify import IdentifyCreditsIntro


class Player(xbmc.Player):
    def __init__(self):
        super().__init__('Player')
        self.intro = None

    def intro_skipped(self):
        self.intro = None

    def onAVStarted(self):
        identify = IdentifyCreditsIntro()
        self.intro = identify.get_intro()
        if self.intro:
            tools.log(
                "Intro detected from {} to {}".format(self.intro[0], self.intro[1]),
                "info",
            )
        else:
            tools.log("No intro could be detected.", "info")

    def onPlayBackStopped(self):
        self.intro = None
