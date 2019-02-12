# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2019  SylvainCecchetto

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

import json
import re
import urlquick

# TO DO
# Add replay


URL_ROOT = 'http://www.lemanbleu.ch'

# Live
URL_LIVE = URL_ROOT + '/fr/Live.html'

URL_INFOMANIAK_LIVE = 'http://livevideo.infomaniak.com/iframe.php?stream=naxoo&name=test&player=%s'
# Player

def live_entry(plugin, item_id, item_dict):
    return get_live_url(plugin, item_id, item_id.upper(), item_dict)


@Resolver.register
def get_live_url(plugin, item_id, video_id, item_dict):

    resp = urlquick.get(URL_LIVE)
    player_id = re.compile(
        r'\&player\=(.*?)\"').findall(resp.text)[0]
    session_urlquick = urlquick.Session(allow_redirects=False)
    resp2 = session_urlquick.get(URL_INFOMANIAK_LIVE % player_id)
    location_url = resp2.headers['Location']
    resp3 = urlquick.get(location_url.replace('infomaniak.com/', 'infomaniak.com/playerConfig.php'), max_age=-1)
    json_parser = json.loads(resp3.text)
    stream_url = ''
    for stram_datas in json_parser['data']['integrations']:
        if 'hls' in stram_datas['type']:
            stream_url = stram_datas['url']
    return stream_url