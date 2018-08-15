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
# Get Image


URL_ROOT = 'http://www.tvm3.tv'

# Replay
URL_REPLAY = URL_ROOT + '/replay'


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

        file_path = utils.get_webcontent(URL_REPLAY)
        replay_shows_soup = bs(file_path, 'html.parser')
        shows_datas = replay_shows_soup.find_all(
            'div', class_='uk-panel uk-panel-hover')

        for show_datas in shows_datas:
            
            show_title = show_datas.find(
                'img').get('alt').encode('utf-8')
            show_image = URL_ROOT + show_datas.find(
                'img').get('src').encode('utf-8')
            show_url = URL_ROOT + show_datas.find(
                'a').get('href').encode('utf-8')

            shows.append({
                'label': show_title,
                'thumb': show_image,
                'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                    action='replay_entry',
                    next='list_videos_1',
                    title=show_title,
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
        episodes = replay_episodes_soup.find_all(
            'div', class_='uk-panel uk-panel-hover uk-invisible')
        episodes += replay_episodes_soup.find_all(
            'div', class_='uk-panel uk-panel-space uk-invisible')

        isyoutube = False

        for episode in episodes:

            video_title = episode.find(
                'h3').find('a').get_text().strip()
            video_duration = 0
            video_id = ''
            if episode.find('div', class_='youtube-player'):
                video_id = episode.find(
                    'div', class_='youtube-player').get('data-id')
                isyoutube = True
            elif episode.find('iframe'):
                video_id = re.compile(
                    r'player.vimeo.com/video/(.*?)\?').findall(episode.find(
                        'iframe').get('src'))[0]
                
            # TO DO Get IMG
            video_img = ''
            # video_img = 'http:' + episode.find(
            #    'img').get('src').encode('utf-8')

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
                    isyoutube = isyoutube,
                    video_id=video_id) + ')'
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
                    video_id=video_id,
                    isyoutube = isyoutube
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
        if params.isyoutube == 'True':
            if params.next == 'download_video':
                return resolver.get_stream_youtube(
                    params.video_id, True)
            else:
                return resolver.get_stream_youtube(
                    params.video_id, False)
        else:
            if params.next == 'download_video':
                return resolver.get_stream_vimeo(
                    params.video_id, True)
            else:
                return resolver.get_stream_vimeo(
                    params.video_id, False)
