# -*- coding: utf-8 -*-
'''
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
'''

import json
import re
from resources.lib import utils
from resources.lib import common


URL_ROOT = 'http://www.elle.fr'

URL_CATEGORIES = URL_ROOT + '/Videos/'

URL_JS_CATEGORIES = 'https://cdn-elle.ladmedia.fr/js/compiled/showcase_bottom.min.js?version=%s'
# IdJsCategories

URL_VIDEOS_JSON = 'https://content.jwplatform.com/v2/playlists/%s'
# CategoryId

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
        URL_CATEGORIES)
    categories_js_id = re.compile(
        r'compiled\/showcase_bottom.min\.js\?version=(.*?)\"').findall(categories_html)[0]
    categories_js_html = utils.get_webcontent(
        URL_JS_CATEGORIES % categories_js_id)
    list_categories = re.compile(
        r'\!0\,playlistId\:\"(.*?)\"').findall(categories_js_html)

    for category_id in list_categories:

        data_categories_json = utils.get_webcontent(
            URL_VIDEOS_JSON % category_id)
        data_categories_jsonparser = json.loads(data_categories_json)
        category_name = data_categories_jsonparser["title"]

        modes.append({
            'label': category_name,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='website_entry',
                category_id=category_id,
                category_name=category_name,
                page='1',
                next='list_videos_1',
                window_title=category_name
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

        replay_episodes_json = utils.get_webcontent(
            URL_VIDEOS_JSON % params.category_id)
        replay_episodes_jsonparser = json.loads(replay_episodes_json)

        for episode in replay_episodes_jsonparser["playlist"]:
            video_title = episode["title"]
            video_url = episode["sources"][0]["file"]
            video_img = episode["image"]
            video_plot = episode["description"]
            video_duration = 0

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
                    action='website_entry',
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
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        content='tvshows',
        category=common.get_window_title(params)
    )


def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_r' or params.next == 'download_video':
        return params.video_url
