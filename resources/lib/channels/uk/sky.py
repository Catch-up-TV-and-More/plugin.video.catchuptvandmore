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

from resources.lib import utils
from resources.lib import common
import re

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.addon.initialize_gettext()

url_live_skynews = 'http://news.sky.com/watch-live'

def channel_entry(params):
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


#@common.plugin.cached(common.cache_time)
def root(params):
    modes = []

    # Add Replay Desactiver
    #modes.append({
    #        'label' : 'Replay',
    #        'url': common.plugin.get_url(
    #            action='channel_entry',
    #            next='list_shows_1',
    #            category='%s Replay' % params.channel_name.upper(),
    #            window_title='%s Replay' % params.channel_name.upper()
    #        ),
    #})

    # Add Live
    modes.append({
        'label' : 'Live TV',
        'url': common.plugin.get_url(
            action='channel_entry',
            next='live_cat',
            category='%s Live TV' % params.channel_name.upper(),
            window_title='%s Live TV' % params.channel_name.upper()
        ),
    })

    return common.plugin.create_listing(
        modes,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
    )

#@common.plugin.cached(common.cache_time)
def list_shows(params):
    shows = []

    return None

#@common.plugin.cached(common.cache_time)
def list_videos(params):
    videos = []

    return None

#@common.plugin.cached(common.cache_time)
def list_live(params):

    lives = []

    title = ''
    subtitle = ' - '
    plot = ''
    duration = 0
    img = ''
    url_live = ''

    title = '%s Live' % (params.channel_name.upper())

    # Get URL Live
    file_path = utils.download_catalog(
        url_live_skynews,
        '%s_live.html' % params.channel_name,
    )
    live_html = open(file_path).read()
    url_live = 'plugin://plugin.video.youtube/?action=play_video&videoid=' + re.compile(r'<iframe src="\/\/www.youtube.com\/embed\/(.*?)\?').findall(live_html)[0]

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
        'url' : common.plugin.get_url(
            action='channel_entry',
            next='play_l',
            url=url_live,
        ),
        'is_playable': True,
        'info': info
    })

    return common.plugin.create_listing(
        lives,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        )
    )

#@common.plugin.cached(common.cache_time)
def get_video_url(params):

    if params.next == 'play_l':
        return params.url

