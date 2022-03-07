import xbmc
import xbmcvfs

import json
import os
import re
import sys
from datetime import time

import importlib

import pysrt

from resources.lib.adapter import PointsAdapter
from resources.lib import settings
from resources.lib import tools


_addons_path = xbmcvfs.translatePath("special://home/addons/")
_a4kSubtitles_id = "service.subtitles.a4ksubtitles"


def get_kodi_subtitle_languages(iso_format=False):
    subtitle_language = tools.execute_jsonrpc(
        "Settings.GetSettingValue", {"setting": "subtitles.languages"}
    )
    if iso_format:
        return [convert_language_iso(x) for x in subtitle_language["value"]]
    else:
        return [x for x in subtitle_language["value"]]


def get_kodi_preferred_subtitle_language(iso_format=False):
    subtitle_language = tools.execute_jsonrpc(
        "Settings.GetSettingValue", {"setting": "locale.subtitlelanguage"}
    )
    if subtitle_language["value"] in ["forced_only", "original", "default", "none"]:
        return subtitle_language["value"]
    if iso_format:
        return convert_language_iso(subtitle_language["value"])
    else:
        return subtitle_language["value"]


def convert_language_iso(from_value):
    return xbmc.convertLanguage(from_value, xbmc.ISO_639_1)


class A4kSubtitlesAdapter(PointsAdapter):
    """
    Ease of use adapter for A4kSubtitles
    """

    def __init__(self, total_time):
        self.subtitle_languages = get_kodi_subtitle_languages()
        self.preferred_language = get_kodi_preferred_subtitle_language()
        self.base_request = {
            "languages": ",".join(self.subtitle_languages),
            "preferredlanguage": self.preferred_language,
        }
        self.total_time = total_time

        self.enabled = False
        if tools.get_condition("System.HasAddon({})".format(_a4kSubtitles_id)):
            self.addon_path = xbmcvfs.translatePath(
                settings.get_addon_info("path", _a4kSubtitles_id)
            )
            self.addon_data = xbmcvfs.translatePath(
                settings.get_addon_info("profile", _a4kSubtitles_id)
            )

            try:
                sys.path.append(self.addon_path)
                self.service = importlib.import_module(
                    "a4kSubtitles.api"
                ).A4kSubtitlesApi()
                self.enabled = True
            except ImportError as e:
                tools.log("Can't find a4kSubtitles: {}".format(e), "error")

    def get_auto_download_enabled(self):
        auto_search = settings.get_setting_boolean(
            "general.auto_search", _a4kSubtitles_id
        )
        auto_download = settings.get_setting_boolean(
            "general.auto_download", _a4kSubtitles_id
        )

        return auto_search and auto_download

    def get_auto_downloaded_subtitles(self):
        last_results = json.loads(
            tools.read_from_file(os.path.join(self.addon_data, "last_results.json"))
        )
        if len(last_results["results"]) == 0:
            return ""

        path = os.path.join(self.addon_data, "temp", last_results["results"][0]["name"])
        if os.path.exists(path):
            tools.log(
                "Using auto-downloaded subtitle file from a4kSubtitles: " + path, "info"
            )

            return path
        else:
            return ""

    def get_points(self, imdb, season, episode, type=None):
        if not self.enabled:
            return None

        if type in ["recap", "intro"]:
            ratio = (0, 0.25)
        elif type in ["commercial"]:
            ratio = (0.25, 0.75)
        elif type in ["outro", "credits"]:
            ratio = (0.75, 1)
        else:
            ratio = (0, 1)

        sub_contents = self._get_subtitle_contents(ratio)
        if not sub_contents:
            return None

        potentials = []
        for i, sub in enumerate(sub_contents):
            gap = self._identify_potential_gap(
                i,
                sub,
                sub_contents[i + 1] if i < (len(sub_contents) - 1) else sub,
            )
            if gap:
                potentials.append(gap)
        return potentials

    def _get_subtitle_contents(self, ratio):
        sub_contents = []

        # if self.get_auto_download_enabled():
        #     download = self.get_auto_downloaded_subtitles()
        # else:
        sub_results = self.search(self.base_request)
        if not sub_results:
            tools.log("No subtitles could be found for the playing file.", "info")
            return []
        download = self.download(sub_results[0])

        if download:
            tools.log("Attempting to identify intro from {}".format(download, "info"))
        else:
            tools.log("Subtitle file could not be found.", "info")
            return []

        sub_contents = pysrt.open(download)
        sub_contents = [
            s
            for s in sub_contents[
                int(len(sub_contents) * ratio[0]) : int(len(sub_contents) * ratio[1])
            ]
            if not any(
                [
                    re.search(
                        i,
                        re.sub(
                            r"\{.*\}|(<\/?\w+((\s+\w+(\s*=\s*(?:\".*?\"|'.*?'|[^'\">\s]+))?)+\s*|\s*)?>)",  # strip formatting tags
                            "",
                            s.text.lower(),
                        ),
                        re.DOTALL,
                    )
                    for i in [
                        r"subtitle|sub|sync|correction|caption",  # attribution
                        r"opensubtitles|subscene|podnadpisi|addic7ed|bsplayer",  # attribution
                        r"(?:^[\(].*[\)]$)|(?:^[\[].*[\]]$)",  # only bracketed text
                        r"(?:^[♩♪♫♬]+$)|(?:^[♩♪♫♬]+.*$)|(?:.*^[♩♪♫♬]+$)",  # lyrics
                        r"(?:^([\W]{1})?.*\1$)",  # anything surrounded by non-word characters
                    ]
                ]
            )
        ]

        return sub_contents

    def _identify_potential_gap(self, index, current_sub, next_sub, threshold=15):
        start = tools.convert_time_to_seconds(current_sub.start.to_time())
        end = tools.convert_time_to_seconds(current_sub.end.to_time())

        if index == 0 and start > threshold:
            return (time(0, 0, 0), current_sub.start.to_time())
        elif index > 0:
            next_start = tools.convert_time_to_seconds(next_sub.start.to_time())

            if (next_start - end) > threshold:
                return (current_sub.end.to_time(), next_sub.start.to_time())

        return ()

    def search(self, request, **extra):
        """
        Search for a subtitle
        :param request: Dictionary containing currently available subtitles and the preferred language
        :type request: dict
        :param extra: Kwargs to provide video meta and settings to A4kSubtitles
        :type extra: dict
        :return: Available subtitle matches
        :rtype: list
        """
        video_meta = extra.pop("video_meta", None)
        settings = extra.pop("settings", None)
        return self.service.search(request, video_meta=video_meta, settings=settings)

    def download(self, request, **extra):
        """
        Downloads requested subtitle
        :param request: Selected subtitle from search results
        :type request: dict
        :param extra: Kwargs, set settings to settings to request to use
        :type extra: dict
        :return: Path to subtitle
        :rtype: str
        """
        try:
            settings = extra.pop("settings", None)
            return self.service.download(request, settings)
        except (OSError, IOError):
            tools.log("Unable to download subtitle, file already exists", "error")
        except Exception as e:
            tools.log("Unknown error acquiring subtitle: {}".format(e), "error")
            tools.log_stacktrace()
