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
from resources.lib import utils
from resources.lib import common

'''
Channels:
    * Franceinfo (Live TV)

TO DO: Replay

'''

SHOW_INFO = 'http://webservices.francetelevisions.fr/tools/' \
            'getInfosOeuvre/v2/?idDiffusion=%s'

LIVE_INFO = 'http://webservices.francetelevisions.fr/tools/' \
            'getInfosOeuvre/v2/?idDiffusion=SIM_%s'

HDFAUTH_URL = 'http://hdfauth.francetv.fr/esi/TA?format=json&url=%s'


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)


@common.PLUGIN.mem_cached(common.CACHE_TIME)
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

        if params.channel_name == 'la_1ere' or \
                params.channel_name == 'france3regions':
            file_prgm = utils.get_webcontent(
                LIVE_INFO % (params.id_stream))
        elif params.channel_name == 'francetvsport':
            file_prgm = utils.get_webcontent(
                SHOW_INFO % (params.id_diffusion))
        else:
            file_prgm = utils.get_webcontent(
                LIVE_INFO % (params.channel_name))

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
