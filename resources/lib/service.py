# -*- coding: utf-8 -*-
import xbmc

from resources.lib import settings
from resources.lib import tools
from resources.lib.player import Player
from resources.lib.skip_dialog import IntroSkipDialog

_addon_path = xbmc.translatePath(settings.get_addon_info('path'))


def run():
    monitor = xbmc.Monitor()
    player = Player()

    while not monitor.abortRequested():
        if monitor.waitForAbort(5):
            # Abort was requested while waiting. We should exit
            break

        if player.isPlayingVideo() and player.intro:
            current_time = player.getTime()

            dialog = IntroSkipDialog(
                "intro_skip_dialog.xml", _addon_path, "Default", "1080i"
            )
            dialog.set_skip_time(player.intro[1])

            if player.intro and current_time >= tools.convert_time_to_seconds(
                player.intro[0]
            ):
                dialog.doModal()
                player.intro_skipped()
            if (
                player.intro
                and current_time >= tools.convert_time_to_seconds(player.intro[1])
            ) or not player.intro:
                dialog.close()
                player.intro_skipped()