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

import re
import ast
import json
import time
from resources.lib import utils
from resources.lib import common


'''
Channels:
    * France TV Sport
'''

SHOW_INFO = 'http://webservices.francetelevisions.fr/tools/' \
            'getInfosOeuvre/v2/?idDiffusion=%s'

URL_ROOT_SPORT = 'https://sport.francetvinfo.fr'

URL_FRANCETV_SPORT = 'https://api-sport-events.webservices.' \
                     'francetelevisions.fr/%s'

HDFAUTH_URL = 'http://hdfauth.francetv.fr/esi/TA?format=json&url=%s'


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
    params['next'] = 'list_shows_ftvsport'
    params['page'] = '1'
    params['mode'] = 'replay'
    params['module_name'] = params.module_name
    params['module_path'] = params.module_path
    return channel_entry(params)


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []

    show_title = 'Videos'
    shows.append({
        'label': show_title,
        'url': common.PLUGIN.get_url(
            module_path=params.module_path,
            module_name=params.module_name,
            action='replay_entry',
            page='1',
            mode='videos',
            title=show_title,
            next='list_videos_ftvsport',
            window_title=show_title
        )
    })

    show_title = 'Replay'
    shows.append({
        'label': show_title,
        'url': common.PLUGIN.get_url(
            module_path=params.module_path,
            module_name=params.module_name,
            action='replay_entry',
            page='1',
            mode='replay',
            title=show_title,
            next='list_videos_ftvsport',
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

    list_videos_html = utils.get_webcontent(
        URL_FRANCETV_SPORT % (params.mode) +
        '?page=%s' % (params.page))
    list_videos_parserjson = json.loads(list_videos_html)

    for video in list_videos_parserjson["page"]["flux"]:

        title = video["title"]
        image = video["image"]["large_16_9"]
        duration = 0
        if 'duration' in video:
            duration = int(video["duration"])
        url_sport = URL_ROOT_SPORT + video["url"]
        html_sport = utils.get_webcontent(url_sport)
        id_diffusion = re.compile(
            r'data-video="(.*?)"').findall(html_sport)[0]

        info = {
            'video': {
                'title': title,
                # 'plot': plot,
                # 'aired': aired,
                # 'date': date,
                'duration': duration,
                # 'year': year,
            }
        }

        download_video = (
            common.GETTEXT('Download'),
            'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                action='download_video',
                module_path=params.module_path,
                module_name=params.module_name,
                id_diffusion=id_diffusion) + ')'
        )
        context_menu = []
        context_menu.append(download_video)

        videos.append({
            'label': title,
            'fanart': image,
            'thumb': image,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='play_r',
                id_diffusion=id_diffusion
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
            mode=params.mode,
            next=params.next,
            page=str(int(params.page) + 1),
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
            common.sp.xbmcplugin.SORT_METHOD_DATE,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
            common.sp.xbmcplugin.SORT_METHOD_EPISODE

        ),
        content='tvshows',
        update_listing='update_listing' in params,
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    lives = []

    title = ''
    plot = ''
    duration = 0

    list_lives = utils.get_webcontent(
        URL_FRANCETV_SPORT % 'directs')
    list_lives_parserjson = json.loads(list_lives)

    if 'lives' in list_lives_parserjson["page"]:

        for live in list_lives_parserjson["page"]["lives"]:
            title = live["title"]
            image = live["image"]["large_16_9"]
            id_diffusion = live["sivideo-id"]

            try:
                value_date = time.strftime(
                    '%d/%m/%Y %H:%M', time.localtime(live["start"]))
            except Exception:
                value_date = ''
            plot = 'Live starts at ' + value_date

            info = {
                'video': {
                    'title': title,
                    'plot': plot,
                    # 'aired': aired,
                    # 'date': date,
                    'duration': duration,
                    # 'year': year,
                }
            }

            lives.append({
                'label': title,
                'fanart': image,
                'thumb': image,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='play_l',
                    id_diffusion=id_diffusion
                ),
                'is_playable': True,
                'info': info
            })

    for live in list_lives_parserjson["page"]["upcoming-lives"]:

        title = live["title"]
        try:
            image = live["image"]["large_16_9"]
        except KeyError:
            image = ''
        # id_diffusion = live["sivideo-id"]

        try:
            value_date = time.strftime(
                '%d/%m/%Y %H:%M', time.localtime(live["start"]))
        except Exception:
            value_date = ''
        plot = 'Live starts at ' + value_date

        info = {
            'video': {
                'title': title,
                'plot': plot,
                # 'aired': aired,
                # 'date': date,
                'duration': duration,
                # 'year': year,
            }
        }

        lives.append({
            'label': title,
            'fanart': image,
            'thumb': image,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='play_l'
            ),
            'is_playable': False,
            'info': info
        })

    return lives


def get_video_url(params):
    """Get video URL and start video player"""

    desired_quality = common.PLUGIN.get_setting('quality')

    if params.next == 'play_r' or params.next == 'download_video':

        file_prgm = utils.get_webcontent(SHOW_INFO % (params.id_diffusion))
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
                    all_datas_videos_path.append(
                        (video['url'], video['drm']))

            seleted_item = common.sp.xbmcgui.Dialog().select(
                common.GETTEXT('Choose video quality'),
                all_datas_videos_quality)

            if seleted_item == -1:
                return None

            url_selected = all_datas_videos_path[seleted_item][0]
            drm = all_datas_videos_path[seleted_item][1]

        elif desired_quality == "BEST":
            for video in json_parser['videos']:
                if video['format'] == 'hls_v5_os':
                    url_selected = video['url']
                    drm = video['drm']
        else:
            for video in json_parser['videos']:
                if video['format'] == 'm3u8-download':
                    url_selected = video['url']
                    drm = video['drm']

        if drm:
            utils.send_notification(
                common.ADDON.get_localized_string(30702))
            return None
        else:
            return url_selected

    elif params.next == 'play_l':

        file_prgm = utils.get_webcontent(
            SHOW_INFO % (params.id_diffusion))

        json_parser = json.loads(file_prgm)

        url_hls_v1 = ''
        url_hls_v5 = ''
        url_hls = ''

        for video in json_parser['videos']:
            if 'format' in video:
                if 'hls_v1_os' in video['format'] and \
                        video['geoblocage'] is not None:
                    url_hls_v1 = video['url']
                if 'hls_v5_os' in video['format'] and \
                        video['geoblocage'] is not None:
                    url_hls_v5 = video['url']
                if 'hls' in video['format']:
                    url_hls = video['url']

        final_url = ''

        # Case France 3 Région
        if url_hls_v1 == '' and url_hls_v5 == '':
            final_url = url_hls
        # Case Jarvis
        if common.sp.xbmc.__version__ == '2.24.0' \
                and url_hls_v1 != '':
            final_url = url_hls_v1
        # Case Krypton, Leia, ...
        if final_url == '' and url_hls_v5 != '':
            final_url = url_hls_v5
        elif final_url == '':
            final_url = url_hls_v1

        file_prgm2 = utils.get_webcontent(HDFAUTH_URL % (final_url))
        json_parser2 = json.loads(file_prgm2)

        return json_parser2['url']
