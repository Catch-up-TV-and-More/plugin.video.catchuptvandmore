# -*- coding: utf-8 -*-
'''
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
'''

import json
import re
from resources.lib import utils
from resources.lib import common

# TO DO
# Get sub-playlist
# Add video info (date, duration)
# Add More video button

URL_ROOT = 'https://www.nytimes.com'

URL_VIDEOS = URL_ROOT + '/video'

URL_PLAYLIST = URL_ROOT + '/svc/video/api/v2/playlist/%s'
# playlistId

URL_STREAM = URL_ROOT + '/svc/video/api/v3/video/%s'
# videoId

def website_entry(params):
    """Entry function of the module"""
    if 'root' in params.next:
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
    """Add modes in the listing"""
    modes = []

    categories_html = utils.get_webcontent(
        URL_VIDEOS)
    categories_datas = re.compile(
        r'var navData =(.*?)\;').findall(categories_html)[0]
    print 'categories_datas value : ' + categories_datas
    categories_jsonparser = json.loads(categories_datas)

    for category in categories_jsonparser:
        category_title = category["display_name"]
        category_playlist = category["knews_id"]

        modes.append({
            'label': category_title,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='website_entry',
                next='list_videos_1',
                title=category_title,
                category_playlist=category_playlist,
                window_title=category_title
            )
        })

    return common.PLUGIN.create_listing(
        modes,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []

    if params.next == 'list_videos_1':

        videos_json = utils.get_webcontent(
            URL_PLAYLIST % params.category_playlist)
        videos_jsonparser = json.loads(videos_json)

        for video_data in videos_jsonparser["videos"]:

            video_title = video_data["headline"]
            video_id = str(video_data["id"])
            video_img = ''
            for image in video_data["images"]:
                video_img = URL_ROOT + '/' + image["url"]
            video_duration = 0
            video_plot = video_data["summary"]

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
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='website_entry',
                    next='play_r',
                    video_id=video_id
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


def get_video_url(params):
    """Get video URL and start video player"""
    video_json = utils.get_webcontent(URL_STREAM % params.video_id)
    video_jsonparser = json.loads(video_json)

    video_url = ''
    for video in video_jsonparser["renditions"]:
        if video["type"] == 'hls':
            video_url = video["url"]
    
    return video_url