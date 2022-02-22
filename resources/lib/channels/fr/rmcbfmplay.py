# -*- coding: utf-8 -*-
# Copyright: (c) 2021, sy6sy2
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

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

def get_token():
    url = "https://sso-client.sfr.fr/cas/services/rest/3.0/createToken.json"
    params = {"duration": 86400}
    headers = {
        "secret": "Basic Y2VjY2hldHRvLnN5bHZhaW5AbWUuY29tOmlQaG9uZTRpUGhvbmU0",
        "Authorization": "Basic Uk1DQkZNUGxheUlPU3YxOnNhdHRvdWYyMDIx",
    }
    resp = urlquick.get(url, params=params, headers=headers).json()
    token = resp["createToken"]["token"]
    return token


def get_account_id(token):
    url = "https://ws-backendtv.rmcbfmplay.com/heimdall-core/public/api/v2/userProfiles"
    params = {
        "app": "bfmrmc",
        "device": "browser",
        "noTracking": "true",
        "token": token,
        "tokenType": "casToken",
    }
    headers = {"User-Agent": USER_AGENT}
    resp = urlquick.get(url, params=params, headers=headers).json()
    account_id = resp["nexttvId"]
    return account_id

API_BACKEND = "https://ws-backendtv.rmcbfmplay.com/gaia-core/rest/api/"
API_CDN_ROOT = "https://ws-cdn.tv.sfr.net/gaia-core/rest/api/"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0"

token = get_token()
account_id = get_account_id(token)

@Route.register
def rmcbfmplay_root(plugin, **kwargs):
    """Root menu of the app."""
    url = API_BACKEND + "web/v1/menu/RefMenuItem::rmcgo_home/structure"
    params = {"app":"bfmrmc","device":"browser","profileId":account_id,"accountTypes":"NEXTTV","operators":"NEXTTV","noTracking":"false"}
    headers = {"User-Agent": USER_AGENT}
    resp = urlquick.get(url, params=params, headers=headers).json() 
    for spot in resp["spots"]:
        item = Listitem()
        item.label = spot["title"]
        item.set_callback(menu, "web/v1/spot/%s/content" % spot["id"])
        item_post_treatment(item)
        yield item

@Route.register
def menu(plugin, path, **kwargs):
    """Menu of the app with v1 API."""

    if "/spot/" in path or "/tile/" in path:
        url = API_BACKEND + path
        params = {"app":"bfmrmc","device":"browser","token":token,"page":"0","size":"30","profileId":account_id,"accountTypes":"NEXTTV","operators":"NEXTTV","noTracking":"false"}
    else:
        url = API_CDN_ROOT + path
        params = {"universe":"PROVIDER","accountTypes":"NEXTTV","operators":"NEXTTV","noTracking":"false"}   

    headers = {"User-Agent": USER_AGENT}
    resp = urlquick.get(url, params=params, headers=headers).json()

    if "items" in resp:
        key = "items"
    elif "spots" in resp:
        key = "spots"
    elif "content" in resp:
        key = "content"
    elif "tiles" in resp:
        key = "tiles"
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

        if key1 and not elt.get('contentType',"").lower() == "movie":
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
            elif "tileId" in elt[key1]["actionIds"]:
                key2 = "tileId"
                subpath = "tile"
            else:
                print("ELT2", elt[key1]["actionIds"], elt)
                continue

            # Find path suffix
            if elt[key1]["actionType"] == "displayStructure":
                suffix = "structure"
            elif elt[key1]["actionType"] == "displayBRContent":
                suffix = "content"
            elif elt[key1]["actionType"] == "displayFip":
                suffix = "episodes"
            else:
                print("ELT3", elt[key1]["actionType"], elt)
                continue

            target_path = "web/v1/%s/%s/%s" % (
                subpath,
                elt[key1]["actionIds"][key2],
                suffix,
            )

            callback = (menu, target_path)
        else:
            _id = elt["id"]
            target_path = "web/v2/content/%s/options" % _id
            callback = (video, target_path, elt["title"])
            # ?app=bfmrmc&device=browser&isProductSeasonWithEpisodes=false&universe=provider

        item = Listitem()
        item.label = elt["title"]
        if "description" in elt:
            item.info["plot"] = elt["description"]
        # TODO: castings, etc

        item.art["thumb"] = ""
        for image in elt["images"]:
            if image["format"] == "1/1" and not item.art["thumb"]:
                item.art["thumb"] = image["url"]
            elif image["format"] == "2/3":
                item.art["thumb"] = image["url"]
            elif image["format"] == "16/9":
                item.art["fanart"] = image["url"]
        item.set_callback(*callback)
        item_post_treatment(item)
        yield item


@Resolver.register
def video(plugin, path, title, **kwargs):
    """Menu of the app with v1 API."""

    # https://ws-cdn.tv.sfr.net/gaia-core/rest/api/web/v1/content/Product::NEUF_BFMTV_BFM0300012711/detail?app=bfmrmc&device=browser&page=0&size=30
    # https://ws-cdn.tv.sfr.net/gaia-core/rest/api/web/v1/content/Product::NEUF_BFMTV_BFM0300012711/detail?app=bfmrmc&device=browser&isProductSeasonWithEpisodes=false&universe=provider
    # https://ws-gaia.tv.sfr.net/gaia-core/rest/api/web/v2/content/Product::NEUF_BFMTV_BFM0300012711/options?app=bfmrmc&device=browser&noTracking=true&token=PIEOVEsvhCYGqC7df4/pvt7TiglWvZqtpW9qdSlvqAyH6bOcdj0JNJmqylF5fws2X29FA1r7isvuWGGhuXpxzGPax1g53%2BuHcPYjHs1z8hkweHk1x2USpCdykMd1wOp%2B5w74DI0c1vl50fZqpCRnR4ppMCbFYhEpThQaLPRvJHgXh7EnJ3IJeJULerWHA%2BjGc&tokenType=casToken&universe=provider
    url = API_CDN_ROOT + path
    params = {
        "app": "bfmrmc",
        "device": "browser",
        "token": token,
        "universe": "provider",
        "accountTypes":"NEXTTV",
        "operators":"NEXTTV",
        "noTracking":"false"
    }

    headers = {"User-Agent": USER_AGENT}
    resp = urlquick.get(url, params=params, headers=headers).json()

    for stream in resp[0]["offers"][0]["streams"]:
        if stream["drm"] == "WIDEVINE":
            item = Listitem()
            item.label = title
            item.path = stream["url"]
            item.property[INPUTSTREAM_PROP] = "inputstream.adaptive"
            item.property["inputstream.adaptive.manifest_type"] = "mpd"
            item.property["inputstream.adaptive.license_type"] = "com.widevine.alpha"
            customdata = "description={}&deviceId=byPassARTHIUS&deviceName=Firefox-92.0--&deviceType=PC&osName=Windows&osVersion=10&persistent=false&resolution=1600x900&tokenType=castoken&tokenSSO={}&entitlementId=3674803340&type=LIVEOTT&accountId={}".format(
                USER_AGENT, token, account_id
            )
            import urllib.parse

            customdata = urllib.parse.quote(customdata)
            item.property["inputstream.adaptive.license_key"] = (
                "https://ws-backendtv.sfr.fr/asgard-drm-widevine/public/licence|User-Agent=" + USER_AGENT + "&customdata="
                + customdata + "&Origin=https://www.rmcbfmplay.com&Content-Type="
                + "|R{SSM}|"
            )
            return item
