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

import json
import re
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common

'''
TODO Add Replay
'''

URL_ROOT = 'https://www.canal10.fr/accueil'

URL_STREAM = 'https://livevideo.infomaniak.com/player_config/%s.json'
# player_id

def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        params.next = 'list_shows_root'
        return list_shows(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)


def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_l':
        live_html = utils.get_webcontent(URL_ROOT)
        player_id = re.compile(
            r'\;player\=(.*?)\"').findall(live_html)[0]
        stream_json = utils.get_webcontent(
            URL_STREAM % player_id)
        stream_jsonparser = json.loads(stream_json)
        return 'https://' + stream_jsonparser["sPlaylist"]
        
