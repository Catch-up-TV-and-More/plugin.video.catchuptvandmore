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
from resources.lib import common

# TO DO

URL_ROOT = 'http://tbd.com'

# Live
URL_LIVE = URL_ROOT

URL_SHOWS = URL_ROOT + '/shows'


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
    """Build categories listing"""
    shows = []

    if params.next == 'list_shows_1':
        shows_html = utils.get_webcontent(
            URL_SHOWS)
        shows_soup = bs(shows_html, 'html.parser')
        list_shows_datas = shows_soup.find_all(
            'a', class_='show-item')

        for show_datas in list_shows_datas:

            show_title = show_datas.get('href').replace('/shows/', '').replace('-', ' ')
            show_url = URL_ROOT + show_datas.get('href')
            show_image = show_datas.find('img').get('src')

            shows.append({
                'label': show_title,
                'thumb': show_image,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    show_url=show_url,
                    title=show_title,
                    next='list_videos_1',
                    window_title=show_title
                )
            })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        category=common.get_window_title(params)
    )

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []

    videos_html = utils.get_webcontent(
        params.show_url)
    videos_soup = bs(videos_html, 'html.parser')
    list_videos_datas = videos_soup.find_all(
        'div', class_='event-item episode')

        
    for video_datas in list_videos_datas:
    
        video_title = video_datas.find('h3').get_text()
        video_duration = 0
        video_url = URL_ROOT + video_datas.find('a').get('href')
        video_img = ''
        for image_datas in video_datas.find_all('img'):
            if 'jpg' in image_datas.get('src'):
                video_img = image_datas.get('src')
        video_plot = ''
        if video_datas.find('p', class_='synopsis'):
            video_plot = video_datas.find('p', class_='synopsis').get_text()
            
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
                video_url=video_url) + ')'
        )
        context_menu = []
        context_menu.append(download_video)

        videos.append({
            'label': video_title,
            'thumb': video_img,
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
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        content='tvshows',
        category=common.get_window_title(params)
    )

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)


def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_r' or params.next == 'download':
        video_html = utils.get_webcontent(
            params.video_url)
        return re.compile(
            r'file\': "(.*?)"').findall(video_html)[0]
    elif params.next == 'play_l':
        live_html = utils.get_webcontent(URL_LIVE)
        return re.compile(
            r'file\': "(.*?)"').findall(live_html)[0]