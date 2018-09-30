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

'''
TODO Add Replay
'''

URL_ROOT = 'http://www.ouatch.tv'

URL_EMISSIONS = URL_ROOT + '/emissions'


def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        params.next = 'list_shows_1'
        return list_shows(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)
    return None

# Dailymotion Id get from these pages below
# - https://www.dailymotion.com/ouatchtv
LIVE_DAILYMOTION_ID = {
    'ouatchtv': 'xuw47s'
}

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []

    if params.next == 'list_shows_1':

        replay_categories_html = utils.get_webcontent(URL_EMISSIONS)
        replay_categories_soup = bs(replay_categories_html, 'html.parser')
        categories = replay_categories_soup.find_all(
            'a', class_='vignepi onglet_emi')

        for category in categories:

            category_name = category.get('title')
            category_img = category.find(
                'img').get('src')
            category_url = category.get('href')
            shows.append({
                'label': category_name,
                'thumb': category_img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    category_url=category_url,
                    category_name=category_name,
                    next='list_videos_1',
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
        list_videos_html = utils.get_webcontent(
            params.category_url)
        list_videos_soup = bs(list_videos_html, 'html.parser')

        videos_data = list_videos_soup.find_all(
            'a', class_=re.compile("mix1 vignepi"))

        for video in videos_data:

            title = video.find_all('p')[0].get_text()
            plot = video.find_all('p')[1].get_text()
            duration = 0
            img = URL_ROOT + video.find_all('img')[0].get('src')
            video_url = video.get('href')

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
                'label': title,
                'thumb': img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='play_r',
                    video_url=video_url,
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
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    params['live_dailymotion_id'] = LIVE_DAILYMOTION_ID[params.channel_name]
    return get_video_url(params)


def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_l':
        return resolver.get_stream_dailymotion(
            params.live_dailymotion_id, False)
    elif params.next == 'play_r' or params.next == 'download_video':
        video_html = utils.get_webcontent(params.video_url)
        video_id = re.compile(
            r'video: "(.*?)"').findall(video_html)[0]
        if params.next == 'download_video':
            return resolver.get_stream_dailymotion(video_id, True)
        else:
            return resolver.get_stream_dailymotion(video_id, False)
