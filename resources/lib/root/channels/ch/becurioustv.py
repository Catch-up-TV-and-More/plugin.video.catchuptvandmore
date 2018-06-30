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
# Add more button
# test videos to see if there is other video hoster


URL_ROOT = 'https://becurious.ch'

URL_VIDEOS = URL_ROOT + '/?infinity=scrolling'

def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        params.next = "list_shows_1"
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'live' in params.next:
        return list_live(params)
    elif 'play' in params.next:
        return get_video_url(params)
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []

    if params.next == 'list_shows_1':

        file_path = utils.get_webcontent(URL_ROOT)
        replay_shows_soup = bs(file_path, 'html.parser')
        shows_datas = replay_shows_soup.find(
            'ul', class_='sub-menu').find_all('li')

        for show_datas in shows_datas:
            
            show_title = show_datas.get_text().encode('utf-8')
            show_url = show_datas.find(
                'a').get('href').encode('utf-8')

            shows.append({
                'label': show_title,
                'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                    action='replay_entry',
                    next='list_videos_1',
                    title=show_title,
                    page=1,
                    show_url=show_url,
                    window_title=show_title
                )
            })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []

    if params.next == 'list_videos_1':
        file_path = utils.get_webcontent(params.show_url)
        replay_episodes_soup = bs(file_path, 'html.parser')
        episodes = replay_episodes_soup.find_all('article')

        for episode in episodes:

            video_title = episode.find('a').get('title').encode('utf-8')
            video_duration = 0
            video_url = episode.find('a').get('href')
            video_img = episode.find('img').get('src')

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
                common.GETTEXT('Download'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='download_video',
                    module_path=params.module_path,
                    module_name=params.module_name,
                    video_url=video_url) + ')'
            )
            context_menu = []
            context_menu.append(download_video)

            videos.append({
                'label': video_title,
                'thumb': video_img,
                'fanart': video_img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
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
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_live_item(params):
    return None


def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_r' or params.next == 'download_video':
        file_path = utils.get_webcontent(params.video_url)
        video_soup = bs(file_path, 'html.parser')
        video_iframe = video_soup.find('iframe')
        
        url_video_resolver = video_iframe.get('src')

        # Case Youtube
        if 'youtube' in url_video_resolver:
            video_id = re.compile(
                'www.youtube.com/embed/(.*?)[\?\"\&]').findall(
                url_video_resolver)[0]
            if params.next == 'download_video':
                return resolver.get_stream_youtube(
                    video_id, True)
            else:
                return resolver.get_stream_youtube(
                    video_id, False)
        # Case Vimeo
        elif 'vimeo' in url_video_resolver:
            video_id = re.compile('player.vimeo.com/video/(.*?)[\?\"]').findall(
                url_video_resolver)[0]
            if params.next == 'download_video':
                return resolver.get_stream_vimeo(
                    video_id, True)
            else:
                return resolver.get_stream_vimeo(
                    video_id, False)
        else:
            # TODO
            return ''
