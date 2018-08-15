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


LIVE_TVP3_REGIONS = {
    "Białystok": "tvp3-bialystok",
    "Bydgoszcz": "tvp3-bydgoszcz",
    "Gdańsk": "tvp3-gdansk",
    "Gorzów Wielkopolski": "tvp3-gorzow-wielkopolski",
    "Katowice": "tvp3-katowice",
    "Kielce": "tvp3-kielce",
    "Kraków": "tvp3-krakow",
    "Lublin": "tvp3-lublin",
    "Łódź": "tvp3-lodz",
    "Olsztyn": "tvp3-olsztyn",
    "Opole": "tvp3-opole",
    "Poznań": "tvp3-poznan",
    "Rzeszów": "tvp3-rzeszow",
    "Szczecin": "tvp3-szczecin",
    "Warszawa": "tvp3-warszawa",
    "Wrocław": "tvp3-wroclaw"
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
        lives_html = utils.get_webcontent(URL_LIVE)
        lives_soup = bs(lives_html, 'html.parser')
        lives_datas = lives_soup.find_all(
            'div', class_=re.compile("button"))
        live_id = ''
        for live_datas in lives_datas:
            if params.module_name == 'tvpinfo':
                if 'info' in live_datas.find('img').get('alt'):
                    live_id = live_datas.get('data-video-id')
            elif params.module_name == 'tvppolonia':
                if 'Polonia' in live_datas.get('data-title'):
                    live_id = live_datas.get('data-video-id')
            elif params.module_name == 'tvp3':
                if LIVE_TVP3_REGIONS[common.PLUGIN.get_setting('tvp3.region')] in live_datas.find('img').get('alt'):
                    live_id = live_datas.get('data-video-id')
        if live_id == '':
            return None
        lives_html = utils.get_webcontent(URL_STREAM % live_id)
        return re.compile(
            r'src:\'(.*?)\'').findall(lives_html)[0]