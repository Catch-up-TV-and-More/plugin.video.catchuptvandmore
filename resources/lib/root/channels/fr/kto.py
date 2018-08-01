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

import ast
import re
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import resolver
from resources.lib import common

'''
TODO Info replays (date, duration, ...)
'''

URL_ROOT = 'http://www.ktotv.com'

URL_SHOWS = URL_ROOT + '/emissions'


def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        params.next = 'list_shows_root'
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

    if params.next == 'list_shows_root':
        videos_categories_html = utils.get_webcontent(
            URL_SHOWS)
        videos_categories_soup = bs(videos_categories_html, 'html.parser')
        videos_categories_list = videos_categories_soup.find_all(
            'span', class_="programTitle")

        for videos_category in videos_categories_list:
            show_title = videos_category.text.encode('utf-8')

            shows.append({
                'label': show_title,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    title=show_title,
                    next='list_shows_videos_1',
                    window_title=show_title
                )
            })

    elif params.next == 'list_shows_videos_1':
        videos_sub_categories_html = utils.get_webcontent(
            URL_SHOWS)
        start = '%s</span>' % params.title.replace("'","&#039;")
        end = '<span class="'
        sub_categories_datas=(videos_sub_categories_html.split(start))[1].split(end)[0]
        sub_categories_datas_soup = bs(sub_categories_datas, 'html.parser')
        sub_categories_list = sub_categories_datas_soup.find_all('a')
        for sub_category in sub_categories_list:
            if 'emissions' in sub_category.get('href'):
                show_title = sub_category.text.encode('utf-8')
                show_url = URL_ROOT + sub_category.get('href')

                shows.append({
                    'label': show_title,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        title=show_title,
                        show_url=show_url,
                        page='1',
                        next='list_videos_1',
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
    if 'previous_listing' in params:
        videos = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_videos_1':

        videos_datas_html = utils.get_webcontent(
            params.show_url + '?page=%s' % (params.page))
        videos_datas_soup = bs(videos_datas_html, 'html.parser')
        videos_datas_list = videos_datas_soup.find_all(
            'div', class_='media-by-category-container')

        if params.page == '1':
            title = videos_datas_soup.find(
                'div', class_="container content").find('a').text.encode('utf-8')
            img = videos_datas_soup.find(
                'div', class_="container content").find('img').get('src')
            url = videos_datas_soup.find(
                'div', class_="container content").find('a').get('href')

            info = {
                'video': {
                    'title': title,
                    # 'aired': aired,
                    # 'date': date,
                    # 'duration': video_duration,
                    # 'year': year,
                    # 'plot': plot,
                    'mediatype': 'tvshow'
                }
            }

            download_video = (
                common.GETTEXT('Download'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='download_video',
                    module_path=params.module_path,
                    module_name=params.module_name,
                    url=url) + ')'
            )
            context_menu = []
            context_menu.append(download_video)

            videos.append({
                'label': title,
                'thumb': img,
                'fanart': img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                     module_name=params.module_name,
                    action='replay_entry',
                    next='play_r',
                    url=url
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

        for video_datas in videos_datas_list:
            title = video_datas.find('img').get('title').encode('utf-8')
            img = video_datas.find('img').get('src').encode('utf-8')
            url = URL_ROOT + video_datas.find('a').get('href')

            info = {
                'video': {
                    'title': title,
                    # 'aired': aired,
                    # 'date': date,
                    # 'duration': video_duration,
                    # 'year': year,
                    # 'plot': plot,
                    'mediatype': 'tvshow'
                }
            }

            download_video = (
                common.GETTEXT('Download'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='download_video',
                    module_path=params.module_path,
                    module_name=params.module_name,
                    url=url) + ')'
            )
            context_menu = []
            context_menu.append(download_video)

            videos.append({
                'label': title,
                'thumb': img,
                'fanart': img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                     module_name=params.module_name,
                    action='replay_entry',
                    next='play_r',
                    url=url
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

        # More videos...
        videos.append({
            'label': common.ADDON.get_localized_string(30700),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next=params.next,
                page=str(int(params.page) + 1),
                show_url=params.show_url,
                title=params.title,
                window_title=params.window_title,
                update_listing=True,
                previous_listing=str(videos)
            )
        })
    
    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE
        ),
        content='tvshows',
        update_listing='update_listing' in params,
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)


def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_l':
        live_html = utils.get_webcontent(URL_ROOT)
        list_url_stream = re.compile(
            r'videoUrl = \'(.*?)\'').findall(
                live_html)
        url_live = ''
        for url_stream_data in list_url_stream:
            if 'm3u8' in url_stream_data:
                url_live = url_stream_data
        return url_live
    elif params.next == 'play_r' or params.next == 'download':
        video_html = utils.get_webcontent(
            params.url)
        video_id = re.compile(
            r'www.youtube.com/embed/(.*?)[\?\"]').findall(video_html)[0]

        if params.next == 'download_video':
            return resolver.get_stream_youtube(video_id, True)
        else:
            return resolver.get_stream_youtube(video_id, False)

