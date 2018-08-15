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
from resources.lib import utils
from resources.lib import common

# TO DO
# Add Replay


URL_ROOT = 'https://www.atresplayer.com/'
# channel name

URL_LIVE_STREAM = 'https://api.atresplayer.com/client/v1/player/live/%s'
# Live Id


def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        params.next = "list_shows_1"
        params["page"] = "0"
        return list_shows(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)


LIVE_ATRES_PLAYER = {
    'antena3': 'ANTENA_3_ID',
    'lasexta': 'LA_SEXTA_ID',
    'neox': 'NEOX_ID',
    'nova': 'NOVA_ID',
    'mega': 'MEGA_ID',
    'atreseries': 'ATRESERIES_ID'
}

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    return None

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)


def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_l':
        file_path = utils.get_webcontent(URL_ROOT)
        lives_json = re.compile(
            r'window.__ENV__ = (.*?)\;').findall(file_path)[0]
        lives_jsonparser = json.loads(lives_json)
        live_stream_json = file_path = utils.get_webcontent(
            URL_LIVE_STREAM % lives_jsonparser[LIVE_ATRES_PLAYER[params.channel_name]]) 
        live_stream_jsonparser = json.loads(live_stream_json)
        if "sources" in live_stream_jsonparser:
            return live_stream_jsonparser["sources"][0]["src"]
        else:
            utils.send_notification(
                common.ADDON.get_localized_string(30713))
            return None
        