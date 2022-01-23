import xbmc
import xbmcvfs

import os
import sys

import importlib

from resources.lib import tools


_addons_path = xbmcvfs.translatePath("special://home/addons/")


def get_kodi_subtitle_languages(iso_format=False):
    subtitle_language = tools.execute_jsonrpc(
        "Settings.GetSettingValue", {"setting": "subtitles.languages"}
    )
    if iso_format:
        return [self.convert_language_iso(x) for x in subtitle_language["value"]]
    else:
        return [x for x in subtitle_language["value"]]

def get_kodi_preferred_subtitle_language(iso_format=False):
    subtitle_language = tools.execute_jsonrpc(
        "Settings.GetSettingValue", {"setting": "locale.subtitlelanguage"}
    )
    if subtitle_language["value"] in ["forced_only", "original", "default", "none"]:
        return subtitle_language["value"]
    if iso_format:
        return self.convert_language_iso(subtitle_language["value"])
    else:
        return subtitle_language["value"]
        

def convert_language_iso(from_value):
    return xbmc.convertLanguage(from_value, xbmc.ISO_639_1)


class A4kSubtitlesAdapter:
    """
    Ease of use adapter for A4kSubtitles
    """

    def __init__(self):
        path = os.path.join(_addons_path, "service.subtitles.a4ksubtitles")
        
        try:
            sys.path.append(path)
            self.service = importlib.import_module("a4kSubtitles.api").A4kSubtitlesApi()
        except ImportError:
            pass

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
            g.log("Unable to download subtitle, file already exists", "error")
        except Exception as e:
            g.log("Unknown error acquiring subtitle: {}".format(e), "error")
            g.log_stacktrace()
