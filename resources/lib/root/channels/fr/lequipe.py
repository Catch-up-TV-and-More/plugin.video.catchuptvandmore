# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2017  SylvainCecchetto

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
import re
from resources.lib import utils
from resources.lib import resolver
from resources.lib import common

# TO DO
# Get Info Live


URL_ROOT = 'https://www.lequipe.fr'

URL_LIVE = URL_ROOT + '/lachainelequipe/'

URL_API_LEQUIPE = URL_ROOT + '/equipehd/applis/filtres/videosfiltres.json'


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
    else:
        return None

CORRECT_MONTH = {
    'janvier.': '01',
    'février.': '02',
    'mars.': '03',
    'avril.': '04',
    'mai.': '05',
    'juin.': '06',
    'juillet.': '07',
    'août.': '08',
    'septembre.': '09',
    'octobre.': '10',
    'novembre.': '11',
    'décembre.': '12'
}

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build shows listing"""
    shows = []

    equipe_categories_json = utils.get_webcontent(URL_API_LEQUIPE)
    equipe_categories_jsonparser = json.loads(equipe_categories_json)

    for categories in equipe_categories_jsonparser['filtres_vod']:
        
        if 'missions' in categories['titre']:
            for category in categories['filters']:
        
                category_name = category['titre']
                category_url = category['filters'].replace('1.json', '%s.json')

                shows.append({
                    'label': category_name,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        category_url=category_url,
                        page='1',
                        category_name=category_name,
                        next='list_videos',
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
    if 'previous_listing' in params:
        videos = ast.literal_eval(params['previous_listing'])

    equipe_videos_json = utils.get_webcontent(
        params.category_url % params.page)
    equipe_videos_jsonparser = json.loads(equipe_videos_json)

    for video_datas in equipe_videos_jsonparser['videos']:

        title = video_datas['titre']
        img = video_datas['src_tablette_retina']
        duration = video_datas['duree']
        video_id = video_datas['lien_dm'].split('//')[1]
        
        date_list = video_datas['date'].split(' ')

        day = '00'
        mounth = '00'
        year = '2018'
        if len(date_list) > 3:
            day = date_list[0]
            try:
                mounth = CORRECT_MONTH[date_list[1]]
            except Exception:
                mounth = '00'
            year = date_list[2]

        date = '.'.join((day, mounth, year))
        aired = '-'.join((year, mounth, day))

        info = {
            'video': {
                'title': title,
                'aired': aired,
                'date': date,
                'duration': duration,
                'year': year,
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
            'fanart': img,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='play_r',
                video_id=video_id
            ),
            'is_playable': True,
            'info': info,
            'context_menu': context_menu
        })

    # More videos...
    if int(params.page) < int(equipe_videos_jsonparser['nb_total_pages']):
        videos.append({
            'label': common.ADDON.get_localized_string(30700),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                category_url=params.category_url,
                category_name=params.category_name,
                next='list_videos',
                page=str(int(params.page) + 1),
                update_listing=True,
                previous_listing=str(videos)
            )
        })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_PLAYCOUNT,
            common.sp.xbmcplugin.SORT_METHOD_DATE,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
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
    if params.next == 'play_r':
        return resolver.get_stream_dailymotion(params.video_id, False)
    elif params.next == 'play_l':
        video_id = ''
        html_live_equipe = utils.get_webcontent(URL_LIVE)
        video_id = re.compile(
            r'dailymotion.com/embed/video/(.*?)[\"\?]',
                re.DOTALL).findall(html_live_equipe)[0]
        return resolver.get_stream_dailymotion(video_id, False)
    elif params.next == 'download_video':
        return resolver.get_stream_dailymotion(params.video_id, True)
