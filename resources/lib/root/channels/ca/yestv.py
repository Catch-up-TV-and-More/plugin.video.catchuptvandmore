# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2017  SylvainCecchetto

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
# Replay add emissions
# Add info LIVE TV

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

URL_LIVE = 'http://www.yestv.com/watch-live/?stream=%s'
# Town

def channel_entry(params):
    """Entry function of the module"""
    if 'root' in params.next:
        return root(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'live' in params.next:
        return list_live(params)
    elif 'play' in params.next:
        return get_video_url(params)
    return None

LIVES_TOWN = {
    'Ontario': 'YESTV-ONT',
    'Alberta': 'YESTV-AB-C'
}

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def root(params):
    """choose mode"""
    modes = []

    # Add Live
    modes.append({
        'label': 'Live TV',
        'url': common.PLUGIN.get_url(
            action='replay_entry',
            next='live_cat',
            category='%s Live TV' % params.channel_name.upper(),
            window_title='%s Live TV' % params.channel_name.upper()
        ),
    })

    return common.PLUGIN.create_listing(
        modes,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title()
    )

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_live(params):
    """Build live listing"""
    lives = []

    title = ''
    plot = ''
    duration = 0
    img = ''
    url_live = ''

    for town_name, live_id in LIVES_TOWN.iteritems():

        title = town_name + ' Live TV'
        live_html = utils.get_webcontent(
            URL_LIVE % live_id)
        url_live_2 = re.compile(
            'iframe src="(.*?) "').findall(live_html)[0]
        live_html_2 = utils.get_webcontent(url_live_2)
        live_json = re.compile(
            'sources\:(.*?)\]\,').findall(live_html_2)[0]
        live_jsonpaser = json.loads(live_json + ']')

        url_live = 'http:' + live_jsonpaser[0]["file"]

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
                action='replay_entry',
                next='play_l',
                url=url_live,
            ),
            'is_playable': True,
            'info': info
        })

    return common.PLUGIN.create_listing(
        lives,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_l':
        return params.url
