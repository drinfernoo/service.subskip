import xbmc
import xbmcvfs

from datetime import time
import json
import os

from resources.lib import settings
from resources.lib import tools

_addon_data = xbmcvfs.translatePath(settings.get_addon_info("profile"))


def get_local_points():
    player = xbmc.Player()

    video_meta = player.getVideoInfoTag()
    imdb_id = str(video_meta.getIMDBNumber())
    season = str(video_meta.getSeason())
    episode = str(video_meta.getEpisode())

    data_points = {}
    file_path = os.path.join(_addon_data, "skip_points", "{}.json".format(imdb_id))
    if not os.path.exists(file_path):
        tools.log("No local skip points found for the playing file.", "info")
        return None

    with open(file_path) as f:
        data_points = json.load(f)

    show_points = data_points.get("show", {})
    season_points = data_points.get("seasons", {}).get(season, {})
    episode_points = season_points.get(episode, {})

    intro = episode_points.get(
        "intro", season_points.get("intro", show_points.get("intro"))
    )
    # outro = episode_points.get("outro", season_points.get("outro", show_points.get("outro")))

    intro_times = []
    if intro:
        intro_times.append(
            (
                time.fromisoformat(intro.get("start", "00:00:00,000000")),
                time.fromisoformat(intro.get("end", "00:00:00,000000")),
            )
        )

    return intro_times
