# -*- coding: utf-8 -*-
import xbmc
import xbmcvfs

from resources.lib import settings
from resources.lib import tools
from resources.lib.player import Player
from resources.lib.skip_dialog import IntroSkipDialog

_addon_path = xbmcvfs.translatePath(settings.get_addon_info('path'))


def run():
    tools.log("Service starting...", "info")
    monitor = xbmc.Monitor()
    player = Player()

    dialog = IntroSkipDialog("intro_skip_dialog.xml", _addon_path, "Default", "1080i")

    while not monitor.abortRequested():
        if monitor.waitForAbort(5):
            # Abort was requested while waiting. We should exit
            break

        if player.isPlayingVideo() and player.intro:
            current_time = player.getTime()
            dialog.set_skip_time(player.intro[1])

            if player.intro and current_time >= tools.convert_time_to_seconds(
                player.intro[0]
            ):
                dialog.show()
            if (
                player.intro
                and current_time >= tools.convert_time_to_seconds(player.intro[1])
            ) or not player.intro:
                dialog.close()
                player.reset_intro()
