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

import json
import re
from resources.lib import utils
from resources.lib import resolver
from resources.lib import common

# TO DO
# Add info LIVE TV
# Get geoblocked video info


URL_ROOT = 'https://videos.tva.ca'

URL_LIVE = URL_ROOT + '/page/direct'

URL_EMISSIONS = URL_ROOT + '/page/touslescontenus'

URL_VIDEOS = URL_ROOT + '/page/rattrapage'


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
    """Build categories listing"""
    shows = []

    if params.next == 'list_shows_1':
        
        category_name = common.ADDON.get_localized_string(30701)
        category_url = URL_VIDEOS
        shows.append({
            'label': category_name,
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

        category_name = 'Tous les contenus'
        shows.append({
            'label': category_name,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                category_name=category_name,
                next='list_shows_2',
                window_title=category_name
            )
        })

    elif params.next == 'list_shows_2':

        replay_categories_html = utils.get_webcontent(URL_EMISSIONS)
        categories = json.loads(
            re.compile(
                r'__INITIAL_STATE__ = (.*?)\}\;').findall(replay_categories_html)[0] + '}')

        for category in categories['items']:
            
            category_name = categories['items'][str(category)]["content"]["attributes"]["title"]
            category_url = URL_ROOT + '/page/' + categories['items'][str(category)]["content"]["attributes"]["pageId"]
            category_img = categories['items'][str(category)]["content"]["attributes"]["image-landscape-medium"].encode('utf-8')
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

        videos_data = json.loads(
            re.compile(
                r'__INITIAL_STATE__ = (.*?)\}\;').findall(list_videos_html)[0] + '}')
        
        data_account = videos_data["configurations"]["accountId"]
        data_player = videos_data["configurations"]["playerId"]

        for video in videos_data['items']:

            if '_' in video:
                title = videos_data['items'][str(video)]["content"]["attributes"]["title"]
                plot = ''
                if 'description' in videos_data['items'][str(video)]["content"]["attributes"]:
                    plot = videos_data['items'][str(video)]["content"]["attributes"]["description"]
                duration = 0
                img = ''
                if 'image-landscape-medium' in videos_data['items'][str(video)]["content"]["attributes"]:
                    img = videos_data['items'][str(video)]["content"]["attributes"]["image-landscape-medium"].encode('utf-8')
                data_video_id = videos_data['items'][str(video)]["content"]["attributes"]["assetId"]

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
                        data_account=data_account,
                        data_player=data_player,
                        data_video_id=data_video_id) + ')'
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
                        data_account=data_account,
                        data_player=data_player,
                        data_video_id=data_video_id,
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
        return resolver.get_brightcove_video_json(
            params.data_account,
            params.data_player,
            params.data_video_id)
    elif params.next == 'play_l':
        live_html = utils.get_webcontent(URL_LIVE)
        data_account = re.compile(
            r'accountId":"(.*?)"').findall(live_html)[0]
        data_player = re.compile(
            r'playerId":"(.*?)"').findall(live_html)[0]
        data_video_id = re.compile(
            r'assetId":"(.*?)"').findall(live_html)[0]
        return resolver.get_brightcove_video_json(
            data_account,
            data_player,
            data_video_id)