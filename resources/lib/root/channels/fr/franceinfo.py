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

import json
import time
from resources.lib import utils
from resources.lib import common

'''
Channels:
    * Franceinfo
    * La 1ère (TODO)
'''

LIVE_INFO = 'http://webservices.francetelevisions.fr/tools/' \
            'getInfosOeuvre/v2/?idDiffusion=SIM_%s'

HDFAUTH_URL = 'http://hdfauth.francetv.fr/esi/TA?format=json&url=%s'

URL_JT_ROOT = 'https://stream.francetvinfo.fr/stream/program/list.json/origin/jt/support/long/page/1/nb/1000'

URL_MAGAZINES_ROOT = 'https://stream.francetvinfo.fr/stream/program/list.json/origin/magazine/support/long/page/1/nb/1000'

URL_AUDIO_ROOT = 'https://stream.francetvinfo.fr/stream/program/list.json/origin/audio/support/long/page/1/nb/1000'

URL_STREAM_ROOT = 'https://stream.francetvinfo.fr'

URL_VIDEOS_ROOT = 'https://stream.francetvinfo.fr/stream/contents/list/videos.json/support/long'

URL_MODULES_ROOT = 'https://stream.francetvinfo.fr/stream/contents/list/videos-selection.json/support/long'

URL_INFO_OEUVRE = 'https://sivideo.webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion=%s&catalogue=Info-web'
# Param : id_diffusion


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

    # Level 0 Root
    if params.next == 'list_shows_root':

        shows.append({
            'label': 'Vidéos',
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='list_videos',
                url=URL_VIDEOS_ROOT,
                window_title='Vidéos'
            )
        })

        shows.append({
            'label': 'Audio',
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='list_shows_sub',
                url=URL_AUDIO_ROOT,
                window_title='Audio'
            )
        })

        shows.append({
            'label': 'JT',
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='list_shows_sub',
                url=URL_JT_ROOT,
                window_title='JT'
            )
        })

        shows.append({
            'label': 'Magazines',
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='list_shows_sub',
                url=URL_MAGAZINES_ROOT,
                window_title='Magazines'
            )
        })

        shows.append({
            'label': 'Modules',
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='list_videos_modules',
                url=URL_MODULES_ROOT,
                window_title='Modules'
            )
        })

    # Level 1 sub
    elif params.next == 'list_shows_sub':

        json_filepath = utils.download_catalog(
            params.url,
            '%s_%s_root.json' % (params.channel_name, params.window_title)
        )
        with open(json_filepath) as json_file:
            json_parser = json.load(json_file)

        for program in json_parser['programs']:
            label = program['label']
            url = URL_STREAM_ROOT + program['url']
            desc = program['description']
            info = {
                'video': {
                    'title': label,
                    'plot': desc
                }
            }
            shows.append({
                'label': label,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='list_videos',
                    url=url,
                    window_title=label
                ),
                'info': info
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

    if 'page' not in params:
        params['page'] = '1'

    json_filepath = utils.download_catalog(
        params.url + '/page/' + params.page,
        '%s_%s_%s_videos.json' % (params.channel_name, params.window_title, params.page)
    )
    with open(json_filepath) as json_file:
        json_parser = json.load(json_file)

    if 'videos' in json_parser:
        list_id = 'videos'
    elif 'contents' in json_parser:
        list_id = 'contents'
    else:
        return None

    for video in json_parser[list_id]:
        title = video['title']
        desc = video['description']
        date_epoch = video['firstPublicationDate']
        url = URL_STREAM_ROOT + video['url']
        for media in video['medias']:
            if 'urlThumbnail' in media:
                icon = URL_STREAM_ROOT + media['urlThumbnail']
                break

        download_video = (
            common.GETTEXT('Download'),
            'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                action='download_video',
                module_path=params.module_path,
                module_name=params.module_name,
                url=url
            ) + ')'
        )
        context_menu = []
        context_menu.append(download_video)

        info = {
            'video': {
                'title': title,
                'plot': desc,
                'aired': time.strftime(
                    '%Y-%m-%d', time.localtime(date_epoch)),
                'date': time.strftime(
                    '%d.%m.%Y', time.localtime(date_epoch)),
                'year': time.strftime(
                    '%Y', time.localtime(date_epoch)),
                'mediatype': 'tvshow'
            }
        }
        videos.append({
            'label': title,
            'thumb': icon,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='play_r',
                url=url
            ),
            'info': info,
            'is_playable': True,
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
            url=params.url,
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

    desired_quality = common.PLUGIN.get_setting('quality')

    if params.next == 'play_r' or params.next == 'download_video':
        stream_infos = json.loads(utils.get_webcontent(params.url))

        method = None
        id_diffusion = ''
        urls = []
        for media in stream_infos['content']['medias']:
            if 'catchupId' in media:
                method = 'id_diffusion'
                id_diffusion = media['catchupId']
                break
            elif 'streams' in media:
                method = 'stream_videos'
                for stream in media['streams']:
                    urls.append((stream['format'], stream['url']))
                break
            elif 'sourceUrl' in media:
                return media['sourceUrl']

        if method == 'id_diffusion':
            json_parser = json.loads(
                utils.get_webcontent(URL_INFO_OEUVRE % id_diffusion))

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

        elif method == 'stream_videos':
            url_hd = ''
            url_default = ''
            for url in urls:
                if 'hd' in url[0]:
                    url_hd = url[1]
                url_default = url[1]

            if desired_quality == "DIALOG":
                items = []
                for url in urls:
                    items.append(url[0])

                seleted_item = common.sp.xbmcgui.Dialog().select(
                    common.GETTEXT('Choose video quality'),
                    items)

                if seleted_item == -1:
                    return None

                url_selected = items[seleted_item][1]

                if url_hd != '':
                    url_selected = url_hd
                else:
                    url_selected = url_default

            else:
                if url_hd != '':
                    url_selected = url_hd
                else:
                    url_selected = url_default

            return url_selected

        else:
            return None

    elif params.next == 'play_l':

        json_parser = json.loads(utils.get_webcontent(
            LIVE_INFO % (params.channel_name)))

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
