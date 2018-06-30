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
URL_LIVE_QVC_FR_IT = 'https://www.qvc.%s/tv/live.html'
# language

URL_LIVE_QVC_JP = 'http://qvc.jp/cont/live/Main'

URL_LIVE_QVC_DE_UK_US = 'http://www.qvc%s/content/shop-live-tv.qvc.html'
# language

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
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)

def get_video_url(params):
    """Get video URL and start video player"""

    desired_language = common.PLUGIN.get_setting(
        params.channel_name + '.language')
    
    if params.next == 'play_l':
        if desired_language == 'FR' or desired_language == 'IT':
            live_html = utils.get_webcontent(
                URL_LIVE_QVC_FR_IT % desired_language.lower())
            live_id = re.compile(
                r'data-media="(.*?)"').findall(live_html)[0]
            live_json = utils.get_webcontent(
                URL_STREAM_LIMELIGHT % live_id)
            live_jsonparser = json.loads(live_json)

            url = ''
            for live_url in live_jsonparser["mediaList"][0]["mobileUrls"]:
                if live_url["targetMediaPlatform"] == "HttpLiveStreaming":
                    url = live_url["mobileUrl"] 
            return url
        elif desired_language == 'JP':
            live_html = utils.get_webcontent(URL_LIVE_QVC_JP)
            return 'http:' + re.compile(
                r'src\', \'(.*?)\'').findall(live_html)[0]           
        elif desired_language == 'DE' or\
            desired_language == 'UK' or\
            desired_language == 'US':
            if desired_language == 'DE':
                live_html = utils.get_webcontent(URL_LIVE_QVC_DE_UK_US % '.de')
            elif desired_language == 'UK':
                live_html = utils.get_webcontent(URL_LIVE_QVC_DE_UK_US % 'uk.com')
            elif desired_language == 'US':
                live_html = utils.get_webcontent(URL_LIVE_QVC_DE_UK_US % '.com')
            live_json = re.compile(
                r'oLiveStreams=(.*?)}},').findall(live_html)[0] + '}}'
            live_jsonparser = json.loads(live_json)
            return 'http:' + live_jsonparser["QVC"]["url"]
