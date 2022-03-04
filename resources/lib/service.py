# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcvfs

from resources.lib import settings
from resources.lib import tools
from resources.lib.player import Player

_addon_data = xbmcvfs.translatePath(settings.get_addon_info("profile"))


def run():
    tools.log("Service starting...", "info")
    monitor = xbmc.Monitor()
    player = Player()
    tools.create_folder(_addon_data)

    while not monitor.abortRequested():
        if monitor.waitForAbort(3):
            # Abort was requested while waiting. We should exit
            break

        if player.isPlayingVideo() and player.get_intro() is not None:
            current_time = player.getTime()
            player.get_dialog().setProperty(
                "skip_time", str(tools.convert_time_to_seconds(player.intro[1]))
            )

            if (
                player.get_intro() is not None
                and not player.get_dialog().isCancelled()
                and current_time >= tools.convert_time_to_seconds(player.intro[0])
                and xbmcgui.getCurrentWindowDialogId() < 13000
            ):
                player.get_dialog().show()
            if (
                player.get_intro() is not None
                and current_time >= tools.convert_time_to_seconds(player.intro[1])
            ) or player.get_intro() is None:
                player.get_dialog().close()
                player.reset_intro()
