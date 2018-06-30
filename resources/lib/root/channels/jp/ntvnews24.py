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
from resources.lib import utils
from resources.lib import resolver
from resources.lib import common

# TO DO
# Add Videos, Replays ?

URL_ROOT = 'http://www.news24.jp'

URL_LIVE = URL_ROOT + '/livestream/'


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
        file_path = utils.get_webcontent(
            URL_LIVE)
        data_account = ''
        data_player = ''
        data_video_id = ''
        if re.compile(
            r'data-account="(.*?)"').findall(file_path) > 0:
            data_account = re.compile(
                r'data-account="(.*?)"').findall(file_path)[0]
            data_player = re.compile(
                r'data-player="(.*?)"').findall(file_path)[0]
            data_video_id = re.compile(
                r'data-video-id="(.*?)"').findall(file_path)[0]
        else:
            data_account = re.compile(
                r'accountId\: "(.*?)"').findall(file_path)[0]
            data_player = re.compile(
                r'player\: "(.*?)"').findall(file_path)[0]
            data_video_id = re.compile(
                r'videoId\: "(.*?)"').findall(file_path)[0]
        return resolver.get_brightcove_video_json(
            data_account,
            data_player,
            data_video_id)
