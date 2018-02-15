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
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common

# TO DO
# Add http://www.rougefm.com/rouge-play/

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()


URL_ROOT = 'http://www.rougefm.com'
# (www or play), channel_name

# Replay
URL_REPLAY = URL_ROOT + '/rouge-tv/'

# Live
URL_LIVE = URL_ROOT + '/rouge-tv/'
# channel_name

URL_LIVE_JSON = 'http://livevideo.infomaniak.com/player_config/%s.json'
# IdLive


def channel_entry(params):
    """Entry function of the module"""
    if 'root' in params.next:
        return root(params)
    elif 'replay_entry' == params.next:
        params.next = "list_shows_1"
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
            page='0',
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

    if params.next == 'list_videos_1':
        file_path = utils.get_webcontent(URL_REPLAY)
        replay_episodes_soup = bs(file_path, 'html.parser')
        episodes = replay_episodes_soup.find_all(
            'div', class_='modal fade replaytv_modal')

        for episode in episodes:

            video_title = episode.find(
                'h4', class_='m-t-30').get_text().strip()
            video_duration = 0
            video_plot = episode.find('p').get_text().strip()
            video_url = episode.find(
                'div', class_='replaytv_video').get('video-src')
            # TO DO Get IMG
            video_img = ''

            info = {
                'video': {
                    'title': video_title,
                    # 'aired': aired,
                    # 'date': date,
                    'duration': video_duration,
                    'plot': video_plot,
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
                'label': video_title,
                'thumb': video_img,
                'fanart': video_img,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='play_r',
                    video_url=video_url
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
            common.sp.xbmcplugin.SORT_METHOD_GENRE,
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        content='tvshows',
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_live(params):
    """Build live listing"""
    lives = []

    title = ''
    # subtitle = ' - '
    plot = ''
    duration = 0
    img = ''
    url_live = ''

    live_html = utils.get_webcontent(URL_LIVE)
    live_id = re.compile(
        'name=rougetv_2015\&player=(.*?)[\"\']').findall(live_html)[0]
    live_json = utils.get_webcontent(URL_LIVE_JSON % live_id)
    lives_json_parser = json.loads(live_json)

    url_live = 'http://' + lives_json_parser["sPlaylist"]
    img = lives_json_parser["preloadimg"]
    title = lives_json_parser["streamname"]

    info = {
        'video': {
            'title': title,
            'plot': plot,
            'duration': duration
        }
    }

    lives.append({
        'label': title,
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
        file_path = utils.get_webcontent(params.video_url)
        url_video = re.compile(
            'source src=\"(.*?)\"').findall(file_path)[0]
        return url_video
    elif params.next == 'play_l':
        return params.url_live
