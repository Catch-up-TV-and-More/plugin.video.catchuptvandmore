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
from resources.lib import common

# TO DO
# Add Replay

# Live
URL_LIVE = 'http://tvpstream.vod.tvp.pl/'


URL_STREAM = 'http://www.tvp.pl/sess/tvplayer.php?object_id=%s'
# videoId


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
    
    lives = []

    title = ''
    # subtitle = ' - '
    plot = ''
    duration = 0
    img = ''
    live_id = ''

    lives_html = utils.get_webcontent(URL_LIVE)
    lives_soup = bs(lives_html, 'html.parser')
    lives_datas = lives_soup.find_all(
        'div', class_=re.compile("button"))
    
    for live_datas in lives_datas:

        title = live_datas.get('data-stationname')
        img = live_datas.find('img').get('src')
        live_id = live_datas.get('data-video-id')

        info = {
            'video': {
                'title': title,
                'plot': plot,
                'duration': duration
            }
        }

        lives.append({
            'label': title,
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
        })
    
    return lives


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_l':
        lives_html = utils.get_webcontent(URL_STREAM % params.live_id)
        return re.compile(
            r'src:\'(.*?)\'').findall(lives_html)[0]