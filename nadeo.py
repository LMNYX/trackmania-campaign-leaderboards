from utils import NadeoUtils
from exceptions import NadeoExceptions
import json
import requests


class NadeoAudiences:
    NadeoServices = "NadeoServices"
    NadeoLiveServices = "NadeoLiveServices"
    NadeoClubServices = "NadeoClubServices"


class NadeoEndpoints:
    NadeoServices = "https://prod.trackmania.core.nadeo.online/v2/"
    NadeoLiveServices = "https://live-services.trackmania.nadeo.live/api/token/"
    NadeoClubServices = "https://club.trackmania.nadeo.live/api/"
    NadeoCompetitionServices = "https://competition.trackmania.nadeo.club/api/"
    NadeoMatchmakingServices = "https://matchmaking.trackmania.nadeo.club/api/"
    TrackmaniaApi = "https://api.trackmania.com/api/"
    Core = "https://prod.trackmania.core.nadeo.online/"


class Nadeo:
    def __init__(self, app_name: str, contact_address: str, audience: str) -> None:
        self.utils = NadeoUtils
        self.base_url = "https://prod.trackmania.core.nadeo.online/v2/"
        self.app_name = app_name
        self.ubi_app_id = "86263886-327a-4328-ac69-527f0d20a237"
        self.contact_address = contact_address
        self.audience = audience
        self.username = None
        self.access_token = None
        self.refresh_token = None
        self.authorized = False

    def api_path(self, url_type: str, *path: str, kwargs: dict = {}):
        return url_type + "/".join(path) + "?" + "&".join([f"{k}={v}" for k, v in kwargs.items()])

    def authenticate(self, login: str, password: str) -> bool:
        b64token = NadeoUtils.basic_auth(login, password)
        r = requests.post(
            "https://public-ubiservices.ubi.com/v3/profiles/sessions", json={"audience": self.audience}, headers={
                "Authorization": f"{b64token}",
                "Ubi-AppId": self.ubi_app_id,
                "User-Agent": f"{self.app_name} / {self.contact_address}"
            })

        if r.status_code == 401:
            raise NadeoExceptions.BadAuthorization(
                "Bad login/password pair or app information.")
        elif r.status_code != 200:
            raise NadeoExceptions.NandOMEGALUL(r.text)
        r = r.json()
        ticket = r["ticket"]
        self.username = r['nameOnPlatform']
        self.profileId = r['profileId']

        r = requests.post(
            self.api_path(NadeoEndpoints.NadeoServices, "authentication", "token", "ubiservices"), json={"audience": self.audience}, headers={
                "Authorization": f"ubi_v1 t={ticket}",
                "Ubi-AppId": self.ubi_app_id,
                "User-Agent": f"{self.app_name} / {self.contact_address}",
                "Content-Type": "application/json"
            })

        if r.status_code == 401:
            raise NadeoExceptions.BadAuthorization(
                "Bad login/password pair or app information.")
        elif r.status_code != 200:
            raise NadeoExceptions.NandOMEGALUL(r.text)

        r = r.json()
        self.access_token = r["accessToken"]
        self.refresh_token = r["refreshToken"]

        return True

    def refresh(self):
        r = requests.post(self.api_path(NadeoEndpoints.NadeoServices, "authentication", "token", "refresh"), headers={
            "Authorization": f"nadeo_v1 t={self.refresh_token}",
            "Ubi-AppId": self.ubi_app_id,
            "User-Agent": f"{self.app_name} / {self.contact_address}"
        }, json={"audience": self.audience})

        if r.status_code == 401:
            raise NadeoExceptions.BadAuthorization(
                "Bad login/password pair or app information.")
        elif r.status_code != 200:
            raise NadeoExceptions.NandOMEGALUL(r.text)

        r = r.json()
        self.access_token = r["accessToken"]
        self.refresh_token = r["refreshToken"]

        return True

    def get_campaigns(self, offset=0, length=1):
        r = requests.get(self.api_path(NadeoEndpoints.NadeoLiveServices, "campaign", "official", kwargs={
            "offset": offset,
            "length": length
        }), headers={
            "Authorization": f"nadeo_v1 t={self.access_token}",
            "Ubi-AppId": self.ubi_app_id,
            "User-Agent": f"{self.app_name} / {self.contact_address}"
        })

        if r.status_code == 401:
            raise NadeoExceptions.BadAuthorization(
                f"Access token has been expired. ({r.text})")
        elif r.status_code != 200:
            raise NadeoExceptions.NandOMEGALUL(r.text)

        return r.json()

    def get_user_id(self, username):
        r = requests.get(self.api_path(NadeoEndpoints.TrackmaniaApi, "display-names", "account-ids", kwargs={
            "displayName[0]": username
        }), headers={
            "Authorization": f"nadeo_v1 t={self.access_token}",
            "Ubi-AppId": self.ubi_app_id,
            "User-Agent": f"{self.app_name} / {self.contact_address}"
        })

        if r.status_code == 401:
            raise NadeoExceptions.BadAuthorization(
                f"Access token has been expired. ({r.text})")
        elif r.status_code != 200:
            raise NadeoExceptions.NandOMEGALUL(r.text)

        return r.json()[username]

    def get_map_info_uid(self, maps):
        r = requests.get(self.api_path(NadeoEndpoints.Core, "maps", kwargs={
            "mapUidList": ','.join(maps)
        }), headers={
            "Authorization": f"nadeo_v1 t={self.access_token}",
            "Ubi-AppId": self.ubi_app_id,
            "User-Agent": f"{self.app_name} / {self.contact_address}"
        })
        if r.status_code == 401:
            raise NadeoExceptions.BadAuthorization(
                f"Access token has been expired. ({r.text})")
        elif r.status_code != 200:
            raise NadeoExceptions.NandOMEGALUL(r.text)

        return r.json()

    def get_map_info_id(self, maps):
        r = requests.get(self.api_path(NadeoEndpoints.Core, "maps", kwargs={
            "mapIdList": ','.join(maps)
        }), headers={
            "Authorization": f"nadeo_v1 t={self.access_token}",
            "Ubi-AppId": self.ubi_app_id,
            "User-Agent": f"{self.app_name} / {self.contact_address}"
        })
        if r.status_code == 401:
            raise NadeoExceptions.BadAuthorization(
                f"Access token has been expired. ({r.text})")
        elif r.status_code != 200:
            raise NadeoExceptions.NandOMEGALUL(r.text)

        return r.json()

    def get_scores(self, maps, userid):
        r = requests.get(self.api_path(NadeoEndpoints.Core, "mapRecords", kwargs={
            "mapIdList": ','.join(maps),
            "accountIdList": userid
        }), headers={
            "Authorization": f"nadeo_v1 t={self.access_token}",
            "Ubi-AppId": self.ubi_app_id,
            "User-Agent": f"{self.app_name} / {self.contact_address}"
        })
        if r.status_code == 401:
            raise NadeoExceptions.BadAuthorization(
                f"Access token has been expired. ({r.text})")
        elif r.status_code != 200:
            raise NadeoExceptions.NandOMEGALUL(r.text)

        return r.json()
