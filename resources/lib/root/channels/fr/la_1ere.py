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
    * La 1ère (JT, Météo, Live TV)

TO DO: Add Emissions

'''

URL_ROOT = 'http://la1ere.francetvinfo.fr'

SHOW_INFO = 'http://sivideo.webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion=%s'
# VideoId

URL_LIVES_JSON = URL_ROOT + '/webservices/mobile/live.json'

URL_JT_JSON = URL_ROOT + '/webservices/mobile/newscast.json?region=%s'
# region

HDFAUTH_URL = 'http://hdfauth.francetv.fr/esi/TA?format=json&url=%s'
# url stream

LIVE_LA1ERE_REGIONS = {
    # New values
    "Guadeloupe": "guadeloupe",
    "Guyane": "guyane",
    "Martinique": "martinique",
    "Mayotte": "mayotte",
    "Nouvelle Calédonie": "nouvellecaledonie",
    "Polynésie": "polynesie",
    "Réunion": "reunion",
    "St-Pierre et Miquelon": "saintpierremiquelon",
    "Wallis et Futuna": "wallisfutuna",
    "Outre-mer": "1ere",
    # Fix possible bug after names changed (not used anymore)
    "Guadeloupe 1ère": "guadeloupe",
    "Guyane 1ère": "guyane",
    "Martinique 1ère": "martinique",
    "Mayotte 1ère": "mayotte",
    "Nouvelle Calédonie 1ère": "nouvellecaledonie",
    "Polynésie 1ère": "polynesie",
    "Réunion 1ère": "reunion",
    "St-Pierre et Miquelon 1ère": "saintpierremiquelon",
    "Wallis et Futuna 1ère": "wallisfutuna"
}

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

        region = LIVE_LA1ERE_REGIONS[common.PLUGIN.get_setting(
            'la_1ere.region')]
        list_jt_json = utils.get_webcontent(
            URL_JT_JSON % region)
        list_jt_jsonkeys = json.loads(list_jt_json).keys()

        for list_jt_name in list_jt_jsonkeys:
            
            print 'list_jt_name :' + list_jt_name.encode('utf-8')

            if list_jt_name != 'mea':
                shows.append({
                    'label': list_jt_name.encode('utf-8'),
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        title=list_jt_name.encode('utf-8'),
                        next='list_videos_1',
                        window_title=list_jt_name.encode('utf-8')
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

    if params.next == 'list_videos_1':
        
        region = LIVE_LA1ERE_REGIONS[common.PLUGIN.get_setting(
            'la_1ere.region')]
        list_videos_jt_json = utils.get_webcontent(
            URL_JT_JSON % region)
        list_videos_jt_jsonparser = json.loads(list_videos_jt_json)
        print 'params.title : ' + params.title

        for video_datas in list_videos_jt_jsonparser[params.title.decode("utf-8", "replace")]:

            title = video_datas["titre"] + ' - ' + video_datas["date"]
            duration = 0
            img = video_datas["url_image"]
            id_diffusion = video_datas["id"]

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
                    id_diffusion=id_diffusion) + ')'
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
                    id_diffusion=id_diffusion,
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
    params['region'] = LIVE_LA1ERE_REGIONS[common.PLUGIN.get_setting(
        'la_1ere.region')]
    return get_video_url(params)


def get_video_url(params):
    """Get video URL and start video player"""

    desired_quality = common.PLUGIN.get_setting('quality')

    if params.next == 'play_r' or params.next == 'download_video':

        json_parser = json.loads(
            utils.get_webcontent(SHOW_INFO % (params.id_diffusion)))

        url_selected = ''

        if 'videos' not in json_parser:
            utils.send_notification(
                common.ADDON.get_localized_string(30710))
            return ''

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

        list_livesid_json = utils.get_webcontent(URL_LIVES_JSON)
        list_livesid_jsonparser = json.loads(list_livesid_json)

        id_sivideo = list_livesid_jsonparser[params.region]["id_sivideo"]

        live_infos_json = utils.get_webcontent(
            SHOW_INFO % id_sivideo.split('@')[0])
        live_infos_jsonparser = json.loads(live_infos_json)

        final_url = ''
        for live_infos in live_infos_jsonparser["videos"]:
            if live_infos["format"] == 'hls':
                final_url = live_infos["url"]

        file_prgm2 = utils.get_webcontent(HDFAUTH_URL % (final_url))
        json_parser2 = json.loads(file_prgm2)

        return json_parser2['url']
