# -*- coding: utf-8 -*-
import xbmc
import xbmcvfs

from resources.lib import settings
from resources.lib import tools
from resources.lib.identifier import Identifier
from resources.lib.skip_dialog import IntroSkipDialog

_addon_path = xbmcvfs.translatePath(settings.get_addon_info('path'))


class Player(xbmc.Player):
    def __init__(self):
        super().__init__("Player")

        self.intro = None
        self.identifier = Identifier()
        self.dialog = IntroSkipDialog(
            "intro_skip_dialog.xml", _addon_path, "Default", "1080i"
        )

    def reset_intro(self):
        self.intro = None

    def get_intro(self):
        return self.intro

    def get_dialog(self):
        return self.dialog

    def onPlayBackStarted(self):
        tools.log("onPlayBackStarted", "debug")
        self.reset_intro()

    def onAVStarted(self):
        tools.log("onAVStarted", "debug")
        video_meta = self.getVideoInfoTag()
        if video_meta.getMediaType() == "episode":
            imdb_id = str(video_meta.getIMDBNumber())
            season = str(video_meta.getSeason())
            episode = str(video_meta.getEpisode())

            intro_point = self.identifier.get_intro(imdb_id, season, episode)
            if intro_point is not None and len(intro_point) >= 1:
                self.intro = intro_point[0]
                tools.log(
                    "Intro detected from {} to {}".format(self.intro[0], self.intro[1]),
                    "info",
                )
            else:
                tools.log("No intro could be detected.", "info")

    def onPlayBackStopped(self):
        tools.log("onPlaybackStopped", "debug")
        self.dialog.close()
        self.reset_intro()
