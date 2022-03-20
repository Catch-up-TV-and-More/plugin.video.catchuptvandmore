# -*- coding: utf-8 -*-
# Copyright: (c) 2019, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import re

import inputstreamhelper

try:  # Python 3
    from urllib.parse import unquote_plus
except ImportError:  # Python 2
    from urllib import unquote_plus

from codequick import Listitem, Resolver, Route
import urlquick
from resources.lib.addon_utils import get_item_media_path, get_quality_YTDL
from resources.lib.kodi_utils import (INPUTSTREAM_PROP, get_selected_item_art,
                                      get_selected_item_info,
                                      get_selected_item_label, get_kodi_version)

# TODO Add Replay

URL_LIVE = 'https://www.bouke.media/direct'

# "live_url":"https:\/\/bouke.fcst.tv\/player\/embed\/3674291"
PATTERN_LIVE_URL = re.compile(r'live_url\":\"(.*?)\"')

# "src":["https:\/\/bouke-live.freecaster.com\/live\/bouke\/bouke.m3u8"]
PATTERN_LIVE_M3U8 = re.compile(r'\"src\":\[\"(.*?\.m3u8)\"\]')


@Route.register
def list_programs(plugin, item_id, **kwargs):
    # TODO
    return False


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "referrer": "https://www.bouke.media/",
    }

    resp = urlquick.get(URL_LIVE, headers=headers, max_age=-1)
    urls = PATTERN_LIVE_URL.findall(resp.text)
    if len(urls) == 0:
        return False

    player_url = unquote_plus(urls[0]).replace("\\", "")
    resp2 = urlquick.get(player_url, max_age=-1)
    m3u8_array = PATTERN_LIVE_M3U8.findall(resp2.text)
    if len(m3u8_array) == 0:
        return False
    url = m3u8_array[0].replace("\\", "")

    if get_kodi_version() < 18:
        quality = get_quality_YTDL(download_mode=False)
        return plugin.extract_source(url, quality)

    is_helper = inputstreamhelper.Helper("hls")
    if not is_helper.check_inputstream():
        quality = get_quality_YTDL(download_mode=False)
        return plugin.extract_source(url, quality)

    item = Listitem()
    item.path = url
    item.property[INPUTSTREAM_PROP] = "inputstream.adaptive"
    item.property["inputstream.adaptive.manifest_type"] = "hls"
    item.label = get_selected_item_label()
    item.art.update(get_selected_item_art())
    item.info.update(get_selected_item_info())

    return item
