# -*- coding: utf-8 -*-
import xbmc
import xbmcgui

from resources.lib import tools
from resources.lib.player import Player


def run():
    tools.log("Service starting...", "info")
    monitor = xbmc.Monitor()
    player = Player()

    while not monitor.abortRequested():
        if monitor.waitForAbort(3):
            # Abort was requested while waiting. We should exit
            break

        if player.isPlayingVideo() and player.intro:
            current_time = player.getTime()
            player.dialog.setProperty(
                "skip_time", str(tools.convert_time_to_seconds(player.intro[1]))
            )

            if (
                player.intro
                and current_time >= tools.convert_time_to_seconds(player.intro[0])
                and xbmcgui.getCurrentWindowDialogId() < 13000
            ):
                player.dialog.show()
            if (
                player.intro
                and current_time >= tools.convert_time_to_seconds(player.intro[1])
            ) or not player.intro:
                player.reset_intro()
