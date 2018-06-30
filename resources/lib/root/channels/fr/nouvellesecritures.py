# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Original work (C) JUL1EN094, SPM, SylvainCecchetto
    Copyright (C) 2016  SylvainCecchetto

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
import json
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import resolver
from resources.lib import common

'''
Channels:
    * IRL
    * Studio 4
'''

SHOW_INFO = 'http://webservices.francetelevisions.fr/tools/' \
            'getInfosOeuvre/v2/?idDiffusion=%s'

URL_ROOT_NOUVELLES_ECRITURES = 'http://%s.nouvelles-ecritures.francetv.fr'
# channel name


def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        return root(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def root(params):
    params['next'] = 'list_shows_necritures_1'
    params['page'] = '1'
    params['mode'] = 'replay'
    params['module_name'] = params.module_name
    params['module_path'] = params.module_path
    return channel_entry(params)


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []
    if 'previous_listing' in params:
        shows = ast.literal_eval(params['previous_listing'])

    if 'list_shows_necritures_1' in params.next:
        categories_html = utils.get_webcontent(
            URL_ROOT_NOUVELLES_ECRITURES % params.channel_name)
        categories_soup = bs(categories_html, 'html.parser')
        categories = categories_soup.find_all(
            'li', class_='genre-item')

        for category in categories:

            category_title = category.find('a').get_text().strip()
            category_data_panel = category.get('data-panel')

            shows.append({
                'label': category_title,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    category_data_panel=category_data_panel,
                    title=category_title,
                    next='list_shows_necritures_2',
                    window_title=category_title
                )
            })

    elif 'list_shows_necritures_2' in params.next:

        shows_html = utils.get_webcontent(
            URL_ROOT_NOUVELLES_ECRITURES % params.channel_name)
        shows_soup = bs(shows_html, 'html.parser')
        class_panel_value = 'panel %s' % params.category_data_panel
        list_shows_necritures = shows_soup.find(
            'div', class_=class_panel_value).find_all('li')

        for show_data in list_shows_necritures:

            show_url = URL_ROOT_NOUVELLES_ECRITURES % params.channel_name + \
                show_data.find('a').get('href')
            show_title = show_data.find('a').get_text().strip()
            show_image = show_data.find('a').get('data-img')

            shows.append({
                'label': show_title,
                'thumb': show_image,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    show_url=show_url,
                    title=show_title,
                    next='list_videos_necritures_1',
                    window_title=show_title
                )
            })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        update_listing='update_listing' in params,
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []

    replay_episodes_html = utils.get_webcontent(
        params.show_url)
    replay_episodes_soup = bs(replay_episodes_html, 'html.parser')
    episodes = replay_episodes_soup.find_all(
        "li", class_="push type-episode")
    episodes += replay_episodes_soup.find_all(
        "li", class_="push type-episode active")

    for episode in episodes:
        if episode.find('div', class_='description'):
            video_title = episode.find(
                'div', class_='title').get_text().strip() + ' - ' + \
                episode.find(
                    'div', class_='description').get_text().strip()
        else:
            video_title = episode.find(
                'div', class_='title').get_text().strip()
        video_url = URL_ROOT_NOUVELLES_ECRITURES % params.channel_name + \
            episode.find('a').get('href')
        if episode.find('img'):
            video_img = episode.find('img').get('src')
        else:
            video_img = ''
        video_duration = 0

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
            common.sp.xbmcplugin.SORT_METHOD_DATE,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
            common.sp.xbmcplugin.SORT_METHOD_EPISODE

        ),
        content='tvshows',
        category=common.get_window_title(params)
    )


def get_video_url(params):
    """Get video URL and start video player"""

    desired_quality = common.PLUGIN.get_setting('quality')

    if params.next == 'play_r' or params.next == 'download_video':

        video_html = utils.get_webcontent(
            params.video_url)
        video_soup = bs(video_html, 'html.parser')
        video_data = video_soup.find(
            'div', class_='player-wrapper')

        if video_data.find('a', class_='video_link'):
            id_diffusion = video_data.find(
                'a', class_='video_link').get(
                    'href').split('video/')[1].split('@')[0]
            file_prgm = utils.get_webcontent(SHOW_INFO % id_diffusion)
            json_parser = json.loads(file_prgm)

            url_selected = ''

            if desired_quality == "DIALOG":
                all_datas_videos_quality = []
                all_datas_videos_path = []

                for video in json_parser['videos']:
                    if video['format'] == 'hls_v5_os' or \
                            video['format'] == 'm3u8-download':
                        if video['format'] == 'hls_v5_os':
                            all_datas_videos_quality.append("HD")
                        else:
                            all_datas_videos_quality.append("SD")
                        all_datas_videos_path.append(video['url'])

                seleted_item = common.sp.xbmcgui.Dialog().select(
                    common.GETTEXT('Choose video quality'),
                    all_datas_videos_quality)

                if seleted_item == -1:
                    return None

                url_selected = all_datas_videos_path[seleted_item]

            elif desired_quality == "BEST":
                for video in json_parser['videos']:
                    if video['format'] == 'hls_v5_os':
                        url_selected = video['url']
            else:
                for video in json_parser['videos']:
                    if video['format'] == 'm3u8-download':
                        url_selected = video['url']

            return url_selected

        else:
            url_video_resolver = video_data.find('iframe').get('src')
            # Case Youtube
            if 'youtube' in url_video_resolver:
                video_id = url_video_resolver.split(
                    'youtube.com/embed/')[1]
                # print 'video_id youtube: ' + video_id
                if params.next == 'download_video':
                    return resolver.get_stream_youtube(
                        video_id, True)
                else:
                    return resolver.get_stream_youtube(
                        video_id, False)
            # Case DailyMotion
            elif 'dailymotion' in url_video_resolver:
                video_id = url_video_resolver.split(
                    'dailymotion.com/embed/video/')[1]
                # print 'video_id dailymotion: ' + video_id
                if params.next == 'download_video':
                    return resolver.get_stream_dailymotion(
                        video_id, True)
                else:
                    return resolver.get_stream_dailymotion(
                        video_id, False)
            else:
                # TO DO add new video hosting ?
                return None

