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
import json
from resources.lib import utils
from resources.lib import resolver
from resources.lib import common

# TO DO
# 

# https://gist.github.com/sergeimikhan/1e90f28b8129335274b9
URL_API_ROOT = 'http://api.beinsports.com'

URL_VIDEOS = URL_API_ROOT + '/contents?itemsPerPage=30&type=3&site=%s&page=%s&order%%5BpublishedAt%%5D=DESC'
# site, page 


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

    desired_language = common.PLUGIN.get_setting(
        params.channel_name + '.language')


    if desired_language == 'FR':
        sites = ['2', '5']
    elif desired_language == 'AU':
        sites = ['1']
    elif desired_language == 'AR':
        sites = ['3']
    elif desired_language == 'EN':
        sites = ['4']
    elif desired_language == 'US':
        sites = ['6']
    elif desired_language == 'ES':
        sites = ['7']
    elif desired_language == 'NZ':
        sites = ['8']
    elif desired_language == 'HK':
        sites = ['10']
    elif desired_language == 'PH':
        sites = ['11']
    elif desired_language == 'TH':
        sites = ['12', '15']
    elif desired_language == 'ID':
        sites = ['13', '14']
    elif desired_language == 'MY':
        sites = ['16']

    if params.next == 'list_shows_1':
        
        for siteid in sites:

            category_name = 'Videos %s (%s)' % (desired_language, siteid)
            category_url = URL_VIDEOS % (siteid, '1')
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

        file_path = utils.get_webcontent(
            params.category_url)
        json_beinsports = json.loads(file_path)

        for episode in json_beinsports['hydra:member']:

            video_title = episode['headline'].encode('utf-8')
            video_plot = ''
            video_duration = 0
            video_id = episode['media'][0]['media']['context']['private_id']
            video_img = episode['media'][0]['media']['context']['thumbnail_url']

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
                    video_id=video_id) + ')'
            )
            context_menu = []
            context_menu.append(download_video)

            videos.append({
                'label': video_title,
                'thumb': video_img,
                'fanart': video_img,
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
        if 'hydra:nextPage' in json_beinsports:
            videos.append({
                'label': '# ' + common.ADDON.get_localized_string(30700),
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='list_videos_1',
                    update_listing=True,
                    category_url=URL_API_ROOT + json_beinsports["hydra:nextPage"],
                    previous_listing=str(videos)
                )
            })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
            common.sp.xbmcplugin.SORT_METHOD_GENRE,
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        content='tvshows',
        update_listing='update_listing' in params,
        category=common.get_window_title(params)
    )

def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_r':
        return resolver.get_stream_dailymotion(params.video_id, False)
    elif params.next == 'download_video':
        return resolver.get_stream_dailymotion(params.video_id, True)