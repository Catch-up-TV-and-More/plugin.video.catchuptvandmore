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
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common

# TO DO
# Add Region
# Check different cases of getting videos

URL_API = 'https://api.radio-canada.ca/validationMedia/v1/Validation.html'

URL_LIVE = URL_API + '?connectionType=broadband&output=json&multibitrate=true&deviceType=ipad&appCode=medianetlive&idMedia=cbuft'

URL_ROOT = 'https://ici.radio-canada.ca'

URL_EMISSION = URL_ROOT + '/tele/emissions' 

URL_STREAM_REPLAY = URL_API + '?connectionType=broadband&output=json&multibitrate=true&deviceType=ipad&appCode=medianet&idMedia=%s'
# VideoId


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
        file_replay = utils.get_webcontent(
            URL_EMISSION)
        file_replay = re.compile(
            r'/\*bns\*/ (.*?) /\*bne\*/').findall(file_replay)[0]
        json_parser = json.loads(file_replay)

        list_emissions = json_parser["teleShowsList"]["pageModel"]["data"]["programmes"]
        list_emissions_regions = json_parser["teleShowsList"]["pageModel"]["data"]["programmesForRegion"]
        
        for emission in list_emissions:
            
            if '/tele/' in emission["link"]:
                emission_name = emission["title"]
                if 'telejournal-22h' in emission["link"] or \
                'telejournal-18h' in emission["link"]:
                    emission_url = emission["link"] + '/2016-2017/episodes'
                else: 
                    emission_url = emission["link"] + '/site/episodes'
                emission_image = emission["pictureUrl"].replace('{0}', '648').replace('{1}', '4x3')

                shows.append({
                    'label': emission_name,
                    'thumb': emission_image,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        next='list_videos_1',
                        emission_url=emission_url,
                        emission_name=emission_name,
                        window_title=emission_name
                    )
                })
        
        for emission in list_emissions_regions:
            
            if '/tele/' in emission["link"]:
                emission_name = emission["title"]
                if 'telejournal-22h' in emission["link"] or \
                'telejournal-18h' in emission["link"]:
                    emission_url = emission["link"] + '/2016-2017/episodes'
                else: 
                    emission_url = emission["link"] + '/site/episodes'
                emission_image = emission["pictureUrl"].replace('{0}', '648').replace('{1}', '4x3')

                shows.append({
                    'label': emission_name,
                    'thumb': emission_image,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        next='list_videos_1',
                        emission_url=emission_url,
                        emission_name=emission_name,
                        window_title=emission_name
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
            params.emission_url)
        list_videos_soup = bs(list_videos_html, 'html.parser')

        if list_videos_soup.find('ul', class_='episodes-container'):
            videos_data = list_videos_soup.find(
                'ul', class_='episodes-container').find_all('li')

            for video in videos_data:
                
                if 'icon-play' in video.find('a').get('class') or \
                    video.find('div', class_='play medium'):
                    title = video.find('a').get('title')
                    plot = ''
                    duration = 0
                    img = ''
                    if video.find('img'):
                        if 'http' in video.find('img').get('src'):
                            img = video.find('img').get('src')
                        else:
                            img = URL_ROOT + video.find('img').get('src')
                    video_url = URL_ROOT + video.find('a').get('href')

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
                            video_url=video_url) + ')'
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
                            video_url=video_url,
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
        live_json = utils.get_webcontent(URL_LIVE)        
        live_jsonparser = json.loads(live_json)
        return live_jsonparser["url"]
    elif params.next == 'play_r' or params.next == 'download':
        video_html = utils.get_webcontent(
            params.video_url)
        video_soup = bs(video_html, 'html.parser')
        video_id = video_soup.find(
            'div', class_='Main-Player-Console').get('id').split('-')[0]
        stream_json = utils.get_webcontent(
            URL_STREAM_REPLAY % video_id)
        stream_jsonparser = json.loads(stream_json)
        return stream_jsonparser["url"]