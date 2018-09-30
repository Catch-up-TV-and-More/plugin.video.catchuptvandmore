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

import re
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import resolver
from resources.lib import common

# TO DO
# Add Replay

# Live
URL_ROOT = 'http://www.%s.tn'
# channel_name


def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        params.next = "list_shows_1"
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
    if params.next == 'play_l':
        root_html = utils.get_webcontent(URL_ROOT % params.channel_name)
        root_soup = bs(root_html, 'html.parser')
        live_url = root_soup.find(
            "section", class_=re.compile('strteamingBlc')).find_all('a')[0].get('href')
        live_html = utils.get_webcontent(live_url)
        live_id_channel = re.compile(
            'www.youtube.com/embed/(.*?)\"').findall(live_html)[1]
        live_youtube_html = utils.get_webcontent( 'https://www.youtube.com/embed/' + live_id_channel)
        live_id = re.compile(
            '\'VIDEO_ID\'\: \"(.*?)\"').findall(live_youtube_html)[0]
        return resolver.get_stream_youtube(live_id, False)