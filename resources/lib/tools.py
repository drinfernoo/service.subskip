# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import xbmc
import xbmcvfs

import json
import os
import shutil
import sys
from xml.etree import ElementTree

from resources.lib import settings

_addon_name = settings.get_addon_info("name")
_addon_id = settings.get_addon_info("id")

_log_levels = {
    "debug": xbmc.LOGDEBUG,
    "info": xbmc.LOGINFO,
    "warning": xbmc.LOGWARNING,
    "error": xbmc.LOGERROR,
    "fatal": xbmc.LOGFATAL,
}


def sleep(ms):
    xbmc.sleep(ms)


def kodi_version():
    return int(xbmc.getInfoLabel("System.BuildVersion")[:2])


def remove_folder(path):
    if xbmcvfs.exists(ensure_path_is_dir(path)):
        log("Removing {}".format(path))
        try:
            shutil.rmtree(path)
        except Exception as e:
            log("Error removing {}: {}".format(path, e))


def remove_file(path):
    if xbmcvfs.exists(path):
        log("Removing {}".format(path))
        try:
            os.remove(path)
        except Exception as e:
            log("Error removing {}: {}".format(path, e))


def read_from_file(file_path):
    try:
        f = xbmcvfs.File(file_path, "r")
        content = f.read()
        return content
    except IOError:
        return None
    finally:
        try:
            f.close()
        except:
            pass


def write_to_file(file_path, content):
    try:
        f = xbmcvfs.File(file_path, "w")
        return f.write(content)
    except IOError:
        return None
    finally:
        try:
            f.close()
        except:
            pass


def parse_xml(file=None, text=None):
    if (file and text) or not (file or text):
        raise ValueError("Incorrect parameters for parsing.")
    if file and not text:
        text = read_from_file(file)

    text = text.strip()
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as e:
        log("Error parsing XML: {}".format(e), level="error")
    return root


def log(msg, level="debug"):
    xbmc.log("[ {} ] {}".format(_addon_id, msg), level=_log_levels[level])


def ensure_path_is_dir(path):
    """
    Ensure provided path string will work for kodi methods involving directories
    :param path: Path to directory
    :type path: str
    :return: Formatted path
    :rtype: str
    """
    if not path.endswith("\\") and sys.platform == "win32":
        if path.endswith("/"):
            path = path.split("/")[0]
        return path + "\\"
    elif not path.endswith("/"):
        return path + "/"
    return path


def create_folder(path):
    path = ensure_path_is_dir(path)
    if not xbmcvfs.exists(path):
        xbmcvfs.mkdir(path)


def get_condition(condition):
    return xbmc.getCondVisibility(condition)


def execute_builtin(bi):
    xbmc.executebuiltin(bi)


def execute_jsonrpc(method, params=None):
    request_data = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": params or {},
    }
    response = json.loads(xbmc.executeJSONRPC(json.dumps(request_data)))
    if "error" in response:
        log(
            "JsonRPC Error {}: {}".format(
                response["error"]["code"], response["error"]["message"]
            ),
            "debug",
        )
    return response.get("result", {})


def convert_time_to_seconds(time_obj):
    return (
        (time_obj.hour * 3600)
        + (time_obj.minute * 60)
        + time_obj.second
        + time_obj.microsecond / 1000000
    )


def levenshteinDistanceDP(token1, token2):
    distances = [[0] * (len(token2) + 1) for _ in range(len(token1) + 1)]

    for t1 in range(len(token1) + 1):
        distances[t1][0] = t1

    for t2 in range(len(token2) + 1):
        distances[0][t2] = t2

    a = 0
    b = 0
    c = 0

    for t1 in range(1, len(token1) + 1):
        for t2 in range(1, len(token2) + 1):
            if token1[t1 - 1] == token2[t2 - 1]:
                distances[t1][t2] = distances[t1 - 1][t2 - 1]
            else:
                a = distances[t1][t2 - 1]
                b = distances[t1 - 1][t2]
                c = distances[t1 - 1][t2 - 1]

                if a <= b and a <= c:
                    distances[t1][t2] = a + 1
                elif b <= a and b <= c:
                    distances[t1][t2] = b + 1
                else:
                    distances[t1][t2] = c + 1

    return distances[len(token1)][len(token2)]
