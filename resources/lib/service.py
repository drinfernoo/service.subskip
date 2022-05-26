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

        intro = player.get_intro()
        if intro is not None and player.isPlayingVideo():
            dialog = player.get_dialog()
            current_time = player.getTime()
            dialog.setProperty(
                "skip_time", str(tools.convert_time_to_seconds(intro[1]))
            )

            if (
                not dialog.isCancelled()
                and current_time >= tools.convert_time_to_seconds(intro[0])
                and xbmcgui.getCurrentWindowDialogId() < 13000
            ):
                dialog.show()
            if current_time >= tools.convert_time_to_seconds(intro[1]):
                dialog.close()
                player.reset_intro()
