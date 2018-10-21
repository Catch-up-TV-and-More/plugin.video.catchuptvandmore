# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2018  SylvainCecchetto

    This file is part of Catch-up TV & More.

    Catch-up TV & More is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    Catch-up TV & More is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with Catch-up TV & More; if not, write to the Free Software Foundation,
    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

# The unicode_literals import only has
# an effect on Python 2.
# It makes string literals as unicode like in Python 3
from __future__ import unicode_literals

from codequick import Route, Resolver, Listitem, utils, Script

from resources.lib.labels import LABELS
from resources.lib import web_utils

from bs4 import BeautifulSoup as bs

import json
import re
import urlquick

# TO DO
# Add Replay


URL_ROOT = 'https://www.atresplayer.com/'
# channel name

URL_LIVE_STREAM = 'https://api.atresplayer.com/client/v1/player/live/%s'
# Live Id


LIVE_ATRES_PLAYER = {
    'antena3': 'ANTENA_3_ID',
    'lasexta': 'LA_SEXTA_ID',
    'neox': 'NEOX_ID',
    'nova': 'NOVA_ID',
    'mega': 'MEGA_ID',
    'atreseries': 'ATRESERIES_ID'
}


def live_entry(plugin, item_id, item_dict):
    return get_live_url(plugin, item_id, item_id.upper(), item_dict)


@Resolver.register
def get_live_url(plugin, item_id, video_id, item_dict):

    resp = urlquick.get(
        URL_ROOT,
        headers={'User-Agent': web_utils.get_random_ua},
        max_age=-1)
    lives_json = re.compile(
        r'window.__ENV__ = (.*?)\;').findall(resp.text)[0]
    json_parser = json.loads(lives_json)
    live_stream_json = urlquick.get(
        URL_LIVE_STREAM % json_parser[LIVE_ATRES_PLAYER[item_id]],
        headers={'User-Agent': web_utils.get_random_ua},
        max_age=-1)
    live_stream_jsonparser = json.loads(live_stream_json.text)
    if "sources" in live_stream_jsonparser:
        return live_stream_jsonparser["sources"][0]["src"]
    else:
        plugin.notify('ERROR', plugin.localize(30713))
        return False
