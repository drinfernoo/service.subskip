# -*- coding: utf-8 -*-
import json
import requests

from resources.lib import settings

_api_key = "REPLACE WITH YOUR OS API KEY"


class OpenSubsApi:
    def __init__(self):
        self._base_url = "https://api.opensubtitles.com/api/v1"
        self._username = settings.get_setting_string("general.username")
        self._password = settings.get_setting_string("general.password")
        self._headers = {
            "User-Agent": "TemporaryUserAgent",
            "Content-Type": "application/json",
            "Api-Key": _api_key,
        }

        self._token = settings.get_setting_string("general.token") or self.login(
            self._username, self._password
        )
        if self._token:
            self._headers["Authorization"] = "Bearer {}".format(self._token)

    def _get(self, endpoint, params={}, data=""):
        url = self._base_url + endpoint
        resp = requests.get(url, headers=self._headers, params=params, data=data)
        return resp.json() if resp.ok else {}

    def _post(self, endpoint, params={}, data=""):
        url = self._base_url + endpoint
        resp = requests.post(url, headers=self._headers, params=params, data=data)
        return resp.json() if resp.ok else {}

    def login(self, username, password):
        resp = self._post(
            "/login", data=json.dumps({"username": username, "password": password})
        )
        token = resp.get("token", "")

        settings.set_setting_string("general.token", token)
        return token

    def search(self, imdb_id, tmdb_id, season, episode):
        return self._get(
            "/subtitles",
            params={
                "parent_imdb_id": imdb_id,
                "parent_tmdb_id": tmdb_id,
                "season_number": season,
                "episode_number": episode,
                "type": "episode",
            },
        )

    def download(self, file_id):
        return self._post(
            "/download",
            data=json.dumps({"file_id": file_id}),
        )
