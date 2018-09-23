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


URL_ROOT = 'https://www.lachainemeteo.com'

URL_VIDEOS = URL_ROOT + '/videos-meteo/videos-la-chaine-meteo'

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


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []

    if params.next == 'list_shows_1':
        programs_html = utils.get_webcontent(URL_VIDEOS)
        programs_soup = bs(programs_html, 'html.parser')
        list_programs = programs_soup.find_all(
            "div", class_="viewVideosSeries")

        for programs_datas in list_programs:
            programs_name = programs_datas.find(
                'div', class_='title').get_text().encode('UTF-8').strip()

            shows.append({
                'label': programs_name,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='list_videos_cat',
                    window_title=programs_name,
                    programs_name=programs_name,
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

    episodes_html = utils.get_webcontent(URL_VIDEOS)
    episodes_soup = bs(episodes_html, 'html.parser')
    list_episodes = episodes_soup.find_all(
        "div", class_="viewVideosSeries")

    for episode in list_episodes:
        programs_name = episode.find(
            'div', class_='title').get_text().encode('UTF-8').strip()
        
        if programs_name == params.programs_name:
            
            list_episodes_datas = episode.find_all('a')
            for episode_datas in list_episodes_datas:
                episode_title = episode_datas.find('div', class_='txt').get_text()
                episode_img = episode_datas.find('img').get('data-src')
                episode_url = episode_datas.get('href')

                info = {
                    'video': {
                        'title': episode_title,
                        # 'plot': plot,
                        # 'episode': episode_number,
                        # 'season': season_number,
                        # 'rating': note,
                        # 'aired': aired,
                        # 'date': date,
                        # 'duration': duration,
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
                        episode_url=episode_url) + ')'
                )
                context_menu = []
                context_menu.append(download_video)

                videos.append({
                    'label': episode_title,
                    'thumb': episode_img,
                    'fanart': episode_img,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        next='play_r',
                        episode_url=episode_url
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
    if params.next == 'play_r' or params.next == 'download_video':
        video_html = utils.get_webcontent(params.episode_url)
        data_account = re.compile(
            'data-account=\'(.*?)\'').findall(video_html)[0]
        data_video_id = re.compile(
            'data-video-id=\'(.*?)\'').findall(video_html)[0]
        data_player = re.compile(
            'data-player=\'(.*?)\'').findall(video_html)[0]
        return resolver.get_brightcove_video_json(
            data_account,
            data_player,
            data_video_id)
        
