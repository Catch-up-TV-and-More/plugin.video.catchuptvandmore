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

# Live
URL_LIVE_QVC_FR = 'https://www.qvc.fr/tv/live.html'

URL_STREAM_LIMELIGHT = 'http://production-ps.lvp.llnw.net/r/PlaylistService/media/%s/getMobilePlaylistByMediaId'
# MediaId


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


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    return None

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_live_item(params):
    title = ''
    # subtitle = ' - '
    plot = ''
    duration = 0
    img = ''
    live_id = ''

    live_html = utils.get_webcontent(URL_LIVE_QVC_FR)
    title = ''
    live_id = re.compile(
        r'data-media="(.*?)"').findall(live_html)[0]

    info = {
        'video': {
            'title': params.channel_label,
            'plot': plot,
            'duration': duration
        }
    }

    return {
        'label': params.channel_label,
        'fanart': img,
        'thumb': img,
        'url': common.PLUGIN.get_url(
            module_path=params.module_path,
            module_name=params.module_name,
            action='start_live_tv_stream',
            next='play_l',
            live_id=live_id
        ),
        'is_playable': True,
        'info': info
    }


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_l':
        live_json = utils.get_webcontent(URL_STREAM_LIMELIGHT % params.live_id)
        live_jsonparser = json.loads(live_json)

        url = ''
        for live_url in live_jsonparser["mediaList"][0]["mobileUrls"]:
            if live_url["targetMediaPlatform"] == "HttpLiveStreaming":
                url = live_url["mobileUrl"] 
        return url