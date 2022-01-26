import xbmc

import re
from datetime import time

from urllib.parse import unquote

import pysrt

from resources.lib import tools
from resources.lib import subtitles
from resources.lib.thread_pool import ThreadPool


class IdentifyCreditsIntro:
    def __init__(self):
        self.a4k_api = subtitles.A4kSubtitlesAdapter()
        self.subtitle_languages = subtitles.get_kodi_subtitle_languages()
        self.preferred_language = subtitles.get_kodi_preferred_subtitle_language()
        self.base_request = {
            "languages": ",".join(self.subtitle_languages),
            "preferredlanguage": self.preferred_language,
        }

        self.initialize()

    def initialize(self):
        self._sub_contents = []
        self._potentials = []
        self.total_time = 0

    def get_intro(self):
        if xbmc.Player().isPlayingVideo():
            self.total_time = xbmc.Player().getTotalTime()

        self._identify_points()

        if len(self._potentials) >= 1:
            return self._potentials[0]

    def _identify_points(self, threshold=15, ratio=0.25):
        self._sub_contents = self._get_subtitles(ratio=ratio)
        if not self._sub_contents:
            return None

        for i, sub in enumerate(self._sub_contents):
            gap = self._identify_potential_gap(
                i,
                sub,
                self._sub_contents[i + 1] if i < (len(self._sub_contents) - 1) else sub,
                threshold=threshold,
                ratio=ratio
            )
            if gap:
                self._potentials.append(gap)

    def _get_subtitles(self, ratio=0.25):
        sub_contents = []

        sub_results = self.a4k_api.search(self.base_request)
        if not sub_results:
            tools.log("No subtitles could be found for the playing file.", "info")
            return []

        download = self.a4k_api.download(sub_results[0])
        if not download:
            tools.log("Subtitle file could not be downloaded.", "info")
            return []
        else:
            tools.log("Attempting to identify intro from {}".format(sub_results[0]["name"], "info"))

        sub_contents = pysrt.open(download)
        sub_contents = [
            s
            for s in sub_contents[: int(len(sub_contents) * ratio)]
            if not any(
                re.search(i, s.text.lower())
                for i in [
                    r"subtitle|sub|sync|correction|caption",
                    r"opensubtitles|subscene|podnadpisi|addic7ed|bsplayer",
                    r"(?:^[\(].*[\)]$)|(?:^[\[].*[\]]$)",
                    r"(?:^[♩♪♫♬]+$)|(?:^[♩♪♫♬]+.*[♩♪♫♬]+$)",
                    r"</?\w+((\s+\w+(\s*=\s*(?:\".*?\"|'.*?'|[^'\">\s]+))?)+\s*|\s*)/?>"
                ]
            )
        ]

        return sub_contents

    def _identify_potential_gap(self, index, current_sub, next_sub, threshold=15, ratio=0.25):
        start = tools.convert_time_to_seconds(current_sub.start.to_time())
        end = tools.convert_time_to_seconds(current_sub.end.to_time())

        if index == 0 and start > threshold:
            return (time(0, 0, 0), current_sub.start.to_time())
        elif index > 0:
            if start < (self.total_time * ratio):
                next_start = tools.convert_time_to_seconds(next_sub.start.to_time())
                next_end = tools.convert_time_to_seconds(next_sub.end.to_time())

                if (next_start - end) > threshold:
                    return (current_sub.end.to_time(), next_sub.start.to_time())

        return ()
