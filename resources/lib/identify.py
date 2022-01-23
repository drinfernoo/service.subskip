import xbmc

import os
from datetime import time

import pysrt

from resources.lib import tools

# from resources.lib.opensubs import OpenSubsApi
from resources.lib import a4ksubs


class IdentifyCreditsIntro:
    def __init__(self):
        self.start_point = None
        self.end_point = None
        # self.os_api = OpenSubsApi()
        self.a4k_api = a4ksubs.A4kSubtitlesAdapter()

        self.subtitle_languages = a4ksubs.get_kodi_subtitle_languages()
        self.preferred_language = a4ksubs.get_kodi_preferred_subtitle_language()
        self.base_request = {
            "languages": ",".join(self.subtitle_languages),
            "preferredlanguage": self.preferred_language,
        }
        self._sub_contents = []
        self._potentials = []
        self.total_time = 0

    def get_intro(self):
        if xbmc.Player().isPlayingVideo():
            self.total_time = xbmc.Player().getTotalTime()

        self._identify_points()

        if len(self._potentials) >= 1:
            return self._potentials[0]

    def _identify_points(self):
        # extract the sub file from the zip
        self._sub_contents = self._get_subtitles()
        if not self._sub_contents:
            return None

        for i, sub in enumerate(self._sub_contents):
            gap = self._identify_potential(i, sub)
            if gap:
                self._potentials.append(gap)

    def _get_subtitles(self):
        sub_contents = []

        sub_results = self.a4k_api.search(self.base_request)
        if not sub_results:
            tools.log("No subtitles could be found for the playing file.", "info")
            return []

        playing_file = xbmc.Player().getPlayingFile()
        current_release = os.path.split(playing_file)[1].lower()

        # TODO: Find a way to match the playing release to the sub we need.
        # subs = [i for i in sub_results if i["attributes"]["release"].lower() in current_release]
        # if not subs:
        # tools.log("A subtitle matching the current release could not be found.", "info")
        # return []

        # sub = sub_results[0]
        # sub_file = sub["attributes"]["files"][0]

        download = self.a4k_api.download(sub_results[0])
        if not download:
            tools.log("Subtitle file could not be downloaded.", "info")
            return []

        sub_contents = pysrt.open(download)

        return sub_contents

    def _identify_potential(self, index, sub, threshold=15):
        start = tools.convert_time_to_seconds(sub.start.to_time())
        end = tools.convert_time_to_seconds(sub.end.to_time())

        if index == 0 and start > threshold:
            return (time(0, 0, 0), sub.start.to_time())
        elif index > 0 and index < (len(self._sub_contents) - 1):
            if start < (self.total_time / 4):
                next_start = tools.convert_time_to_seconds(
                    self._sub_contents[index + 1].start.to_time()
                )
                next_end = tools.convert_time_to_seconds(
                    self._sub_contents[index + 1].end.to_time()
                )

                if (next_start - end) > threshold:
                    return (
                        sub.end.to_time(),
                        self._sub_contents[index + 1].start.to_time(),
                    )

        return ()
