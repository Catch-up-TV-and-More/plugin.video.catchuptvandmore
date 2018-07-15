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
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common

# TO DO
# Fix Video 404 / other type stream video (detect and implement)

URL_ROOT = 'https://abcnews.go.com'

# Stream
URL_LIVE_STREAM = URL_ROOT + '/video/itemfeed?id=abc_live11&secure=true'

URL_REPLAY_STREAM = URL_ROOT + '/video/itemfeed?id=%s'
# videoId


def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        params.next = "list_shows_1"
        params["page"] = "0"
        return list_shows(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []

    if params.next == 'list_shows_1':
        shows_html = utils.get_webcontent(
            URL_ROOT)
        shows_soup = bs(shows_html, 'html.parser')
        list_shows_datas = shows_soup.find(
            'div', class_='shows-dropdown').find_all(
                'li')

        for show_datas in list_shows_datas:

            show_title = show_datas.find('span', class_='link-text').get_text()
            show_url = show_datas.find('a').get('href')

            shows.append({
                'label': show_title,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    title=show_title,
                    show_url=show_url,
                    next='list_videos_1',
                    window_title=show_title
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

    episodes_html = utils.get_webcontent(
        params.show_url)
    episodes_soup = bs(episodes_html, 'html.parser')
    list_episodes_datas = {}
    if episodes_soup.find(
        'article', class_='carousel-item row-item fe-top'):
        list_episodes_datas = episodes_soup.find(
            'article', class_='carousel-item row-item fe-top').find_all(
                'div', class_='item')

    for episode_datas in list_episodes_datas:
    
        video_title = ''
        if episode_datas.find(
            'img').get('alt'):
            video_title = episode_datas.find(
                'img').get('alt').replace('VIDEO: ', '')
        video_duration = 0
        video_id = episode_datas.find('figure').get('data-id')
        video_img = episode_datas.find('img').get('data-src')
            
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
                action='replay_entry',
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


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)


def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_l':
        url_live = ''
        live_json = utils.get_webcontent(URL_LIVE_STREAM)
        live_jsonparser = json.loads(live_json)
        for url_live_data in live_jsonparser["channel"]["item"]["media-group"]["media-content"]:
            if 'application/x-mpegURL' in url_live_data["@attributes"]["type"]:
                if 'preview' not in url_live_data["@attributes"]["url"]:
                    url_live = url_live_data["@attributes"]["url"]
        return url_live
    elif params.next == 'play_r' or params.next == 'download':
        stream_json = utils.get_webcontent(
            URL_REPLAY_STREAM % params.video_id)
        stream_jsonparser = json.loads(stream_json)
        url_stream = ''
        for stream_data in stream_jsonparser["channel"]["item"]["media-group"]["media-content"]:
            if stream_data["@attributes"]["type"] == 'application/x-mpegURL':
                url_stream = stream_data["@attributes"]["url"]
        return url_stream
