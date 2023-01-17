from nadeo import Nadeo, NadeoAudiences
from trackmania import Trackmania
from utils import NadeoUtils
import os
import time
import dotenv

dotenv.load_dotenv()

nadeo = Nadeo(os.getenv("UBI_APP_NAME"), os.getenv("UBI_APP_CONTACT"),
              NadeoAudiences.NadeoLiveServices)
nadeocore = Nadeo(os.getenv("UBI_APP_NAME"), os.getenv("UBI_APP_CONTACT"),
                  NadeoAudiences.NadeoServices)

if not nadeo.authenticate(os.getenv("UBI_LOGIN"), os.getenv("UBI_PASSWORD")):
    print("Authentication failed.")
    exit(1)
if not nadeocore.authenticate(os.getenv("UBI_LOGIN"), os.getenv("UBI_PASSWORD")):
    print("Authentication failed.")
    exit(1)

ids = {
    "LilyIsInsane": nadeo.get_user_id("LilyIsInsane"),
    "Styx_on_osu": nadeo.get_user_id("Styx_on_osu")
}

campaign = nadeo.get_campaigns()['campaignList'][0]


def get_users():
    return ids


def get_maps():
    refresh_token()
    campaign = nadeo.get_campaigns()['campaignList'][0]
    maps = map(lambda x: x['mapUid'], campaign['playlist'])
    maps = nadeocore.get_map_info_uid(maps)
    _maps = []

    for _map in maps:
        _maps.append({
            "name": _map['name'],
            "id": _map['mapId'],
            "thumbnail": _map['thumbnailUrl'],
            "times": {
                "author": _map['authorScore'],
                "gold": _map['goldScore'],
                "silver": _map['silverScore'],
                "bronze": _map['bronzeScore']
            }
        })

    _maps.sort(key=lambda x: x['name'])

    return _maps


def get_scores(ids, _maps):

    scores = {}
    for user in ids:
        _tempScores = nadeocore.get_scores(
            list(map(lambda x: x['id'], _maps)), ids[user])
        scores[user] = {}

        _tempScores.sort(key=lambda x: list(
            filter(lambda y: y['id'] == x['mapId'], _maps))[0]['name'])

        for score in _tempScores:
            scores[user][score['mapId']] = {
                "name": list(filter(lambda x: x['id'] == score['mapId'], _maps))[0]['name'],
                "time": score['recordScore']['time'],
                "medal": score['medal'],
                "timestamp": score['timestamp']
            }

    return scores


def refresh_token():
    # if token is about to expire
    ndata = NadeoUtils.read_token(nadeo.refresh_token)
    ncdata = NadeoUtils.read_token(nadeo.refresh_token)

    if ndata['exp'] - time.time() < 60:
        nadeo.refresh_token()
    if ncdata['exp'] - time.time() < 60:
        nadeocore.refresh_token()

    return True
