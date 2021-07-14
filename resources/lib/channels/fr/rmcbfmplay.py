# -*- coding: utf-8 -*-
# Copyright: (c) 2021, sy6sy2
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import json
import re
from builtins import str

import inputstreamhelper
import urlquick
from codequick import Listitem, Resolver, Route, Script
from kodi_six import xbmcgui
from resources.lib import download, web_utils
from resources.lib.addon_utils import get_item_media_path
from resources.lib.kodi_utils import (INPUTSTREAM_PROP, get_kodi_version,
                                      get_selected_item_art,
                                      get_selected_item_info,
                                      get_selected_item_label)
from resources.lib.menu_utils import item_post_treatment

API_GAIA_ROOT = "https://ws-gaia.tv.sfr.net/gaia-core/rest/api/"
API_CDN_ROOT = "https://ws-cdn.tv.sfr.net/gaia-core/rest/api/"
USER_AGENT = "BFMRMC - 1.0.1 - iPhone9,3 - mobile - iOS 14.2"


def get_token():
    url = "https://sso-client.sfr.fr/cas/services/rest/3.0/createToken.json"
    params = {"duration": 86400}
    headers = {
        "secret": "Basic Y2VjY2hldHRvLnN5bHZhaW5AbWUuY29tOmlQaG9uZTRpUGhvbmU0",
        "Authorization": "Basic Uk1DQkZNUGxheUlPU3YxOnNhdHRvdWYyMDIx",
    }
    resp = urlquick.get(url, params=params, headers=headers).json()
    token = resp["createToken"]["token"]
    print("TOKEN: " + token)
    return token


def get_account_id(token):
    url = "https://ws-heimdall.tv.sfr.net/heimdall-core/public/api/v2/userProfiles"
    params = {
        "app": "bfmrmc",
        "device": "ios",
        "noTracking": "true",
        "token": token,
        "tokenType": "casToken",
    }
    headers = {"User-Agent": USER_AGENT}
    resp = urlquick.get(url, params=params, headers=headers).json()
    account_id = resp["nexttvId"]
    print("ACCOUNTID: " + account_id)
    return account_id


@Route.register
def rmcbfmplay_root(plugin, **kwargs):
    """Root menu of the app."""
    url = API_GAIA_ROOT + "bfmrmc/mobile/v1/explorer/structure"
    params = {"app": "bfmrmc", "device": "ios"}
    headers = {"User-Agent": USER_AGENT}
    resp = urlquick.get(url, params=params, headers=headers).json()
    for spot in resp["spots"]:
        item = Listitem()
        item.label = spot["title"]
        item.set_callback(menu, "mobile/v2/spot/%s/content" % spot["id"])
        item_post_treatment(item)
        yield item


@Route.register
def menu(plugin, path, **kwargs):
    """Menu of the app with v2 API."""
    url = API_GAIA_ROOT + path
    params = {"app": "bfmrmc", "device": "ios", "page": 0, "size": 30}
    headers = {"User-Agent": USER_AGENT}
    resp = urlquick.get(url, params=params, headers=headers).json()

    if "items" in resp:
        key = "items"
    elif "spots" in resp:
        key = "spots"
    elif "content" in resp:
        key = "content"
    else:
        print("RESP", resp)

    for elt in resp[key]:

        # Find key 1
        if "more" in elt:
            key1 = "more"
        elif "action" in elt:
            key1 = "action"
        else:
            print("ELT1", elt)
            key1 = None

        if key1:
            if not elt[key1]["actionIds"]:
                continue

            # Find key 2
            if "menuId" in elt[key1]["actionIds"]:
                key2 = "menuId"
                subpath = "menu"
            elif "spotId" in elt[key1]["actionIds"]:
                key2 = "spotId"
                subpath = "spot"
            elif "contentId" in elt[key1]["actionIds"]:
                key2 = "contentId"
                subpath = "content"
            else:
                print("ELT2", elt[key1]["actionIds"], elt)
                continue

            # Find path suffix
            if elt[key1]["actionType"] == "displayStructure":
                suffix = "structure"
            elif elt[key1]["actionType"] == "displayContent":
                suffix = "more"
            elif elt[key1]["actionType"] == "displayFip":
                suffix = "episodes"
            else:
                print("ELT3", elt[key1]["actionType"], elt)
                continue

            target_path = "mobile/v2/%s/%s/%s" % (
                subpath,
                elt[key1]["actionIds"][key2],
                suffix,
            )
            callback = (menu, target_path)
        else:
            _id = elt["id"]
            target_path = "mobile/v3/content/%s/options" % _id
            callback = (video, target_path)
            # ?app=bfmrmc&device=ios&isProductSeasonWithEpisodes=false&universe=provider

        item = Listitem()
        item.label = elt["title"]
        if "description" in elt:
            item.info["plot"] = elt["description"]
        # TODO: castings, etc

        item.art["thumb"] = ""
        try:
            for image in elt["images"]:
                if image["format"] == "1/1" and not item.art["thumb"]:
                    item.art["thumb"] = image["url"]
                elif image["format"] == "2/3":
                    item.art["thumb"] = image["url"]
                elif image["format"] == "16/9":
                    item.art["fanart"] = image["url"]
        except Exception:
            pass
        item.set_callback(*callback)
        item_post_treatment(item)
        yield item


@Resolver.register
def video(plugin, path, **kwargs):
    """Menu of the app with v2 API."""

    # https://ws-cdn.tv.sfr.net/gaia-core/rest/api/mobile/v2/content/Product::NEUF_BFMTV_BFM0300012711/detail?app=bfmrmc&device=ios&page=0&size=30
    # https://ws-cdn.tv.sfr.net/gaia-core/rest/api/mobile/v2/content/Product::NEUF_BFMTV_BFM0300012711/detail?app=bfmrmc&device=ios&isProductSeasonWithEpisodes=false&universe=provider
    # https://ws-gaia.tv.sfr.net/gaia-core/rest/api/mobile/v3/content/Product::NEUF_BFMTV_BFM0300012711/options?app=bfmrmc&device=ios&noTracking=true&token=PIEOVEsvhCYGqC7df4/pvt7TiglWvZqtpW9qdSlvqAyH6bOcdj0JNJmqylF5fws2X29FA1r7isvuWGGhuXpxzGPax1g53%2BuHcPYjHs1z8hkweHk1x2USpCdykMd1wOp%2B5w74DI0c1vl50fZqpCRnR4ppMCbFYhEpThQaLPRvJHgXh7EnJ3IJeJULerWHA%2BjGc&tokenType=casToken&universe=provider
    url = API_CDN_ROOT + path
    params = {
        "app": "bfmrmc",
        "device": "ios",
        "tokenType": "casToken",
        "universe": "provider",
        "token": get_token(),
    }

    headers = {"User-Agent": USER_AGENT}
    resp = urlquick.get(url, params=params, headers=headers).json()
    print("RESP_VIDEO", resp)
    for stream in resp[0]["offers"][0]["streams"]:
        if stream["drm"] == "WIDEVINE":
            print("COUCOU")
            item = Listitem()
            item.path = stream["url"]
            item.property[INPUTSTREAM_PROP] = "inputstream.adaptive"
            item.property["inputstream.adaptive.manifest_type"] = "mpd"
            item.property["inputstream.adaptive.license_type"] = "com.widevine.alpha"
            token = get_token()
            account_id = get_account_id(token)
            customdata = "sec-fetch-site=cross-site&sec-fetch-mode=cors&sec-fetch-dest=empty&user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36&description=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36&deviceId=byPassARTHIUS&deviceName=Chrome-91.0.4472.114---&deviceType=PC&osName=Mac OS&osVersion=10.15.7&persistent=false&resolution=2048x1280&tokenType=castoken&tokenSSO={}&entitlementId=3606640421&type=LIVEOTT&accountId={}".format(
                token, account_id
            )
            import urllib.parse

            customdata = urllib.parse.quote(customdata)
            item.property["inputstream.adaptive.license_key"] = (
                "https://ws-backendtv.sfr.fr/asgard-drm-widevine/public/licence|user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36&customdata="
                + customdata
                + "|R{SSM}|"
            )
            return item
