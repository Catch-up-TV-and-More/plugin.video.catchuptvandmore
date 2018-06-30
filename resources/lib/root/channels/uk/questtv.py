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
# 

URL_ROOT = 'https://www.questtv.co.uk'

URL_VIDEOS = URL_ROOT + '/content/discovery/neur/uk/questtv/video/jcr:content/root/columns_container_1/column1/brightcove_video_lis.content'

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
    """Build shows listing"""
    shows = []

    if params.next == 'list_shows_1':

        all_video = common.ADDON.get_localized_string(30701)

        shows.append({
            'label': common.GETTEXT('All videos'),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='list_videos_1',
                page=1,
                all_video=all_video,
                window_title=all_video
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
        list_videos_html = utils.get_webcontent(
            URL_VIDEOS)
        list_videos_soup = bs(list_videos_html, 'html.parser')

        data_account = list_videos_soup.find(
            'video').get('data-account')
        data_player = list_videos_soup.find(
            'video').get('data-player')

        videos_datas = list_videos_soup.find_all(
            'div', class_=re.compile("dni-video-playlist-thumb-box"))

        for video_datas in videos_datas:

            video_title = video_datas.find('h3', class_="descHidden").get_text()

            video_duration = 0
            video_plot = video_datas.find('p', class_="descHidden").get_text()
            video_img = video_datas.find('img').get('src')
            data_video_id = video_datas.find('a').get('href').replace('#', '')

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
                common.GETTEXT('Download'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='download_video',
                    module_path=params.module_path,
                    module_name=params.module_name,
                    data_account=data_account,
                    data_player=data_player,
                    data_video_id=data_video_id) + ')'
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
                    data_account=data_account,
                    data_player=data_player,
                    data_video_id=data_video_id
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
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
        return resolver.get_brightcove_video_json(
            params.data_account,
            params.data_player,
            params.data_video_id)
