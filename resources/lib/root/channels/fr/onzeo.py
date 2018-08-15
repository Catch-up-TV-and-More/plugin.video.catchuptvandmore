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
# ....


URL_ROOT = 'http://www.onzeo.fr/'


def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        params.next = "list_shows_1"
        return list_shows(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build shows listing"""
    shows = []

    if params.next == 'list_shows_1':

        list_categories_html = utils.get_webcontent(
            URL_ROOT)
        list_categories_soup = bs(list_categories_html, 'html.parser')
        categories = list_categories_soup.find_all(
            'section', class_='une2')

        for category in categories:
            
            if category.get('style') is None:
                category_name = category.find(
                    'h2', class_='titreBloc').get_text()
                category_id = category.find(
                    'div', class_=re.compile("zoneb")).get('id')
                shows.append({
                    'label': category_name,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        next='list_videos_1',
                        category_id=category_id,
                        category_name=category_name,
                        window_title=category_name
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
        list_categories_html = utils.get_webcontent(
            URL_ROOT)
        list_categories_soup = bs(list_categories_html, 'html.parser')

        categories = list_categories_soup.find_all(
            'div', class_=re.compile("zoneb"))

        for category in categories:

            if params.category_id == category.get('id'):

                datas_videos = category.find_all('div', class_='cell item')
                for datas_video in datas_videos:
                    title = datas_video.find('h2').get_text()
                    duration = 0
                    img = datas_video.find('img').get('src')
                    video_id = datas_video.get('iddm')

                    info = {
                        'video': {
                            'title': title,
                            # 'plot': plot,
                            # 'aired': aired,
                            # 'date': date,
                            'duration': duration,
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
                            video_id=video_id) + ')'
                    )
                    context_menu = []
                    context_menu.append(download_video)

                    videos.append({
                        'label': title,
                        'thumb': img,
                        'url': common.PLUGIN.get_url(
                            module_path=params.module_path,
                            module_name=params.module_name,
                            action='replay_entry',
                            next='play_r',
                            video_id=video_id,
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
        update_listing='update_listing' in params,
        category=common.get_window_title(params)
    )


def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_r':
        return resolver.get_stream_dailymotion(params.video_id, False)
    elif params.next == 'download_video':
        return resolver.get_stream_dailymotion(params.video_id, True)
