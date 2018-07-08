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

import ast
import json
import re
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import resolver
from resources.lib import common

# TO DO

URL_ROOT = 'https://www.onf.ca'

URL_VIDEOS = URL_ROOT + '/remote/explorer-tous-les-films/?language=fr&genre=%s&availability=free&sort_order=publication_date&page=%s'
# Genre, Page

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

GENRE_VIDEOS = {
    '64': 'Actualité (1940-1965)',
    '61': 'Animation',
    '30500': 'Documentaire',
    '62': 'Expérimental',
    '59': 'Fiction',
    '63': 'Film pour enfants',
    '60': 'Long métrage de fiction',
    '89': 'Multimédia interactif'
}


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def root(params):
    """Add modes in the listing"""
    modes = []

    for category_id, category_title in GENRE_VIDEOS.iteritems():
        
        modes.append({
            'label': category_title,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='website_entry',
                next='list_videos_1',
                page='1',
                title=category_title,
                category_id=category_id,
                window_title=category_title
            )
        })

    return common.PLUGIN.create_listing(
        modes,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_LABEL,
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []
    if 'previous_listing' in params:
        videos = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_videos_1':

        replay_episodes_json = utils.get_webcontent(
            URL_VIDEOS % (params.category_id, params.page))
        replay_episodes_jsonparser = json.loads(replay_episodes_json)
        for replay_episodes_datas in replay_episodes_jsonparser["items_html"]:
            list_episodes_soup = bs(replay_episodes_datas, 'html.parser')
            list_episodes = list_episodes_soup.find_all('li')

            for episode in list_episodes:
                video_title = episode.find(
                    'img').get('alt')
                video_url = URL_ROOT + episode.find('a').get('href')
                video_img = episode.find(
                    'img').get('src')
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
                        action='website_entry',
                        next='play_r',
                        video_url=video_url
                    ),
                    'is_playable': True,
                    'info': info,
                    'context_menu': context_menu
                })

        # More videos...
        videos.append({
            'label': '# ' + common.ADDON.get_localized_string(30700),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='website_entry',
                next='list_videos_1',
                category_id=params.category_id,
                page=str(int(params.page) + 1),
                update_listing=True,
                previous_listing=str(videos)
            )
        })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        content='tvshows',
        update_listing='update_listing' in params,
        category=common.get_window_title(params)
    )


def get_video_url(params):
    """Get video URL and start video player"""

    video_html = utils.get_webcontent(params.video_url)
    # Get DailyMotion Id Video
    video_url = re.compile(
        r'og\:video\:url" content="(.*?)"').findall(
        video_html)[0]
    if params.next == 'play_r':
        return resolver.get_stream_kaltura(video_url, False)
    elif params.next == 'download_video':
        return resolver.get_stream_kaltura(video_url, True)