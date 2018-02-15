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

import ast
import re
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import resolver
from resources.lib import common

# TO DO
# ...

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

URL_ROOT = 'http://www.gongnetworks.com'

URL_LIVE = URL_ROOT + '/gong.php'

URL_VIDEOS = URL_ROOT + '/videos.php?page=%s'
# Page


def channel_entry(params):
    """Entry function of the module"""
    if 'root' in params.next:
        return root(params)
    elif 'replay_entry' == params.next:
        params.next = "list_videos_1"
        return list_shows(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'live' in params.next:
        return list_live(params)
    elif 'play' in params.next:
        return get_video_url(params)
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def root(params):
    """Add Replay and Live in the listing"""
    modes = []

    # Add Replay
    modes.append({
        'label': 'Replay',
        'url': common.PLUGIN.get_url(
            action='channel_entry',
            next='list_videos_1',
            page='1',
            category='%s Replay' % params.channel_name.upper(),
            window_title='%s Replay' % params.channel_name
        )
    })

    # Add Live
    modes.append({
        'label': _('Live TV'),
        'url': common.PLUGIN.get_url(
            action='channel_entry',
            next='live_cat',
            category='%s Live TV' % params.channel_name.upper(),
            window_title='%s Live TV' % params.channel_name
        )
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
    """Build videos listing"""
    videos = []
    if 'previous_listing' in params:
        videos = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_videos_1':
        list_videos_html = utils.get_webcontent(
            URL_VIDEOS % (params.page))
        list_videos_soup = bs(list_videos_html, 'html.parser')

        videos_data = list_videos_soup.find_all(
            'div', class_=re.compile("preview"))

        for video in videos_data:

            title = video.find('img').get('alt')
            plot = ''
            duration = 0
            img = URL_ROOT + '/' + video.find('img').get('src')
            video_url = URL_ROOT + '/' + video.find('a').get('href')

            info = {
                'video': {
                    'title': title,
                    'plot': plot,
                    # 'aired': aired,
                    # 'date': date,
                    'duration': duration,
                    # 'year': year,
                    'mediatype': 'tvshow'
                }
            }

            download_video = (
                _('Download'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='download_video',
                    video_url=video_url) + ')'
            )
            context_menu = []
            context_menu.append(download_video)

            videos.append({
                'label': title,
                'thumb': img,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='play_r',
                    video_url=video_url,
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

        # More videos...
        videos.append({
            'label': common.ADDON.get_localized_string(30100),
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='list_videos_1',
                page=str(int(params.page) + 1),
                update_listing=True,
                previous_listing=str(videos)
            )
        })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        content='tvshows',
        update_listing='update_listing' in params,
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_live(params):
    """Build live listing"""
    lives = []

    title = ''
    plot = ''
    duration = 0
    img = ''
    url_live = ''

    file_path = utils.get_webcontent(URL_LIVE)

    url_live = re.compile(
        r'x-mpegurl" src="(.*?)"').findall(file_path)[0]

    title = '%s Live' % params.channel_name.upper()

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
            action='channel_entry',
            next='play_l',
            url_live=url_live,
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
    if params.next == 'play_r' or params.next == 'download_video':
        video_html = utils.get_webcontent(params.video_url)
        video_id = re.compile(
            r'videoId: \'(.*?)\'').findall(video_html)[0]
        if params.next == 'download_video':
            return resolver.get_stream_youtube(video_id, True)
        else:
            return resolver.get_stream_youtube(video_id, False)
    elif params.next == 'play_l':
        return params.url_live
