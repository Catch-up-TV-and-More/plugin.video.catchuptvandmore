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

import base64
import json
import re
from resources.lib import utils
from resources.lib import common

# TO DO
# Replay

URL_ROOT = 'https://www.heart.co.uk'

URL_LIVE_ID = URL_ROOT + '/tv'

URL_VIDEO_VOD = 'https://player.ooyala.com/sas/player_api/v2/authorization/' \
                'embed_code/%s/%s?device=html5&domain=www.channelnewsasia.com'
# pcode, liveId

URL_GET_JS_PCODE = 'https://player.ooyala.com/core/%s'
# playeId


def channel_entry(params):
    """Entry function of the module"""
    if 'list_shows' in params.next:
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
        stream_html = utils.get_webcontent(
            URL_LIVE_ID)
        live_id = re.compile(
            'div id="ooyala_(.*?)"').findall(stream_html)[0]
        player_id = re.compile(
            'player.ooyala.com/core/(.*?)"').findall(stream_html)[0]
        stream_pcode = utils.get_webcontent(
            URL_GET_JS_PCODE % player_id)
        pcode = re.compile(
            'internal.playerParams.pcode=\'(.*?)\'').findall(stream_pcode)[0]
        stream_json = utils.get_webcontent(
            URL_VIDEO_VOD % (pcode, live_id))
        stream_jsonparser = json.loads(stream_json)
        # Get Value url encodebase64
        for stream in stream_jsonparser["authorization_data"][live_id]["streams"]:
            if stream["delivery_type"] == 'hls':
                url_base64 = stream["url"]["data"]
        return base64.standard_b64decode(url_base64)
