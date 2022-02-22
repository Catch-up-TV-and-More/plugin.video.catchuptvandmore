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

API_ROOT = "https://ws-gaia.tv.sfr.net/gaia-core/rest/api/"
USER_AGENT = "BFMRMC - 1.0.1 - iPhone9,3 - mobile - iOS 14.2"


@Route.register
def rmcbfmplay_root(plugin, **kwargs):
    """Root menu of the app."""
    url = API_ROOT + "bfmrmc/mobile/v1/explorer/structure"
    params = {"app": "bfmrmc", "device": "ios"}
    headers = {"User-Agent": USER_AGENT}
    resp = urlquick.get(url, params=params, headers=headers).json()
    for spot in resp["spots"]:
        item = Listitem()
        item.label = spot["title"]
        item.set_callback(second_level, spot["id"])
        item_post_treatment(item)
        yield item


@Route.register
def second_level(plugin, _id, **kwargs):
    """Second level of the app (channels and thematics)."""
    url = API_ROOT + "mobile/v2/spot/%s/content"
    params = {"app": "bfmrmc", "device": "ios"}
    headers = {"User-Agent": USER_AGENT}
    resp = urlquick.get(url % _id, params=params, headers=headers).json()
    for elt in resp["items"]:
        item = Listitem()
        item.label = elt["title"]
        try:
            item.art["thumb"] = elt["images"][0]["url"]
        except Exception:
            pass
        item.set_callback(third_level, elt["id"])
        item_post_treatment(item)
        yield item


@Route.register
def third_level(plugin, _id, **kwargs):
    return False
