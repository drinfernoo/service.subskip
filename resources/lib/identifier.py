import xbmc

from resources.lib import settings
from resources.lib.local_points import LocalPointsAdapter
from resources.lib.subtitles import A4kSubtitlesAdapter

_use_a4ksubs = settings.get_setting_boolean("general.use_a4ksubs")


class Identifier:
    def __init__(self):
        self.player = xbmc.Player()

    def get_intro(self, imdb_id, season, episode):
        self.adapter = LocalPointsAdapter()
        local_points = self.adapter.get_points(imdb_id, season, episode, "intro")
        # db_points = self._get_db_points()

        if local_points:
            return local_points[0]
        else:
            if _use_a4ksubs:
                total_time = xbmc.Player().getTotalTime()
                self.adapter = A4kSubtitlesAdapter(total_time)
                return self.adapter.get_points(imdb_id, season, episode, "intro")

        return None
