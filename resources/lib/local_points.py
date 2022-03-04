import xbmc
import xbmcvfs

from datetime import time
import json
import os

from resources.lib.adapter import PointsAdapter
from resources.lib import settings
from resources.lib import tools

_addon_data = xbmcvfs.translatePath(settings.get_addon_info("profile"))


class LocalPointsAdapter(PointsAdapter):
    def __init__(self):
        pass

    def get_points(self, imdb_id, season, episode, type=None):
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

        point = episode_points.get(type, season_points.get(type, show_points.get(type)))

        point_times = []
        if point:
            point_times.append(
                (
                    time.fromisoformat(point.get("start", "00:00:00,000000")),
                    time.fromisoformat(point.get("end", "00:00:00,000000")),
                )
            )

        return point_times
