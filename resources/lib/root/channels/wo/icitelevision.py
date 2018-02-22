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

import re
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import resolver
from resources.lib import common

# TO DO

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

URL_ROOT = 'http://icitelevision.ca'

URL_EMISSION = 'http://icitelevision.ca/emissions/'

URL_LIVE = 'http://icitelevision.ca/live-video/'


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
    else:
        return None


# @common.PLUGIN.mem_cached(common.CACHE_TIME)
def root(params):
    """Add Replay and Live in the listing"""
    modes = []

    # Add Replay
    modes.append({
        'label': 'Replay',
        'url': common.PLUGIN.get_url(
            action='channel_entry',
            next='list_shows_1',
            category='%s Replay' % params.channel_name.upper(),
            window_title='%s Replay' % params.channel_name.upper()
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


# @common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []

    if params.next == 'list_shows_1':

        # Get Emission :
        root_html = utils.get_webcontent(
            URL_EMISSION)
        root_soup = bs(root_html, 'html.parser')
        emissions_soup = root_soup.find_all(
            'div', class_="fusion-column-wrapper")

        for emission in emissions_soup:

            if emission.find('h3'):
                emission_name = emission.find('h3').find(
                    'a').get_text().encode('utf-8')
                emission_img = emission.find('img').get(
                    'src').encode('utf-8')
                emission_url = emission.find('a').get(
                    'href').encode('utf-8')

                if 'http' not in emission_url:
                    emission_url = URL_ROOT + '/' + emission_url

                shows.append({
                    'label': emission_name,
                    'thumb': emission_img,
                    'url': common.PLUGIN.get_url(
                        action='channel_entry',
                        emission_url=emission_url,
                        category_name=emission_name,
                        next='list_videos_1',
                        window_title=emission_name
                    )
                })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title()
    )

# @common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []

    if params.next == 'list_videos_1':
        file_path = utils.get_webcontent(params.emission_url)
        replay_episodes_soup = bs(file_path, 'html.parser')
        episodes = replay_episodes_soup.find_all(
            'div', class_='youtube_gallery_item')

        for episode in episodes:

            video_title = episode.find('a').get('title')
            video_duration = 0
            video_url = episode.find('a').get('href')
            video_img = episode.find_all('img')[1].get('src')

            info = {
                'video': {
                    'title': video_title,
                    # 'aired': aired,
                    # 'date': date,
                    'duration': video_duration,
                    # 'plot': video_plot,
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

# @common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_live(params):
    """Build live listing"""
    lives = []

    title = ''
    plot = ''
    duration = 0
    img = ''
    url_live = ''

    live_html = utils.get_webcontent(URL_LIVE)
    title = 'ICI en direct'
    url_live = re.compile(
        'source src=\"(.*?)\"').findall(live_html)[0]
    img = re.compile(
        'poster=\"(.*?)\"').findall(live_html)[0]

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


# @common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_l':
        return params.url_live
    elif params.next == 'play_r' or params.next == 'download_video':
        # Case Youtube
        if 'youtube' in params.video_url:
            video_id = re.compile(
                'www.youtube.com/embed/(.*?)[\?\"\&]').findall(
                params.video_url)[0]
            if params.next == 'download_video':
                return resolver.get_stream_youtube(
                    video_id, True)
            else:
                return resolver.get_stream_youtube(
                    video_id, False)
        # Case Vimeo
        elif 'vimeo' in params.video_url:
            video_id = re.compile('player.vimeo.com/video/(.*?)[\?\"\&]').findall(
                params.video_url)[0]
            if params.next == 'download_video':
                return resolver.get_stream_vimeo(
                    video_id, True)
            else:
                return resolver.get_stream_vimeo(
                    video_id, False)
