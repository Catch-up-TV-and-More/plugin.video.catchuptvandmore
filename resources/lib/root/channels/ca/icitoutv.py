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
# Add emissions
# Some videos not working
# Some videos protected by drm
# some videos are paid video (add account ?)

URL_ROOT = 'https://services.radio-canada.ca' 

URL_EMISSION = URL_ROOT + '/toutv/presentation/CatchUp?device=web&version=4'

URL_STREAM_REPLAY = URL_ROOT + '/media/validation/v2/?connectionType=hd&output=json&multibitrate=true&deviceType=ipad&appCode=toutv&idMedia=%s'
# VideoId

URL_CLIENT_KEY_JS = 'https://ici.tou.tv/app.js'
# To GET client-key for menu

URL_CLIENT_KEY_VIDEO_JS = URL_ROOT + '/media/player/client/toutv_beta'
# TODO Get client key for 

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

        client_key_html = utils.get_webcontent(URL_CLIENT_KEY_JS)
        client_key_value = 'client-key %s' % re.compile(
            r'scope\:\{clientId\:\"(.*?)\"').findall(client_key_html)[0]
        specific_headers_data = {
            'Authorization': client_key_value
        }
        file_replay = utils.get_webcontent(
            URL_EMISSION, specific_headers=specific_headers_data)
        json_parser = json.loads(file_replay)

        list_days = json_parser["Lineups"]
        
        for day in list_days:
            
            day_name = day["Title"]
            day_id = day["Name"]

            shows.append({
                'label': day_name,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='list_videos_1',
                    day_id=day_id,
                    day_name=day_name,
                    window_title=day_name
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
        file_replay = utils.get_webcontent(
            URL_EMISSION, specific_headers={'Authorization': 'client-key 4dd36440-09d5-4468-8923-b6d91174ad36'})
        json_parser = json.loads(file_replay)
        list_days = json_parser["Lineups"]

        for day in list_days:
            
            if day["Name"] == params.day_id:

                for video in day["LineupItems"]:
                    if video["IsFree"] and video["IsDrm"] is False:
                        title = video["ProgramTitle"] + ' ' + video["HeadTitle"]
                        plot = video["Description"]
                        duration = 0
                        img = video["ImageUrl"].replace('w_200,h_300', 'w_300,h_200')
                        video_id = video["IdMedia"]

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
                                video_id=video_id) + ')'
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
                                video_id=video_id,
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
    if params.next == 'play_r' or params.next == 'download':

        client_key_html = utils.get_webcontent(URL_CLIENT_KEY_VIDEO_JS)
        client_key_value = 'client-key %s' % re.compile(
            r'prod\"\,clientKey\:\"(.*?)\"').findall(client_key_html)[0]
        specific_headers_data = {
            'Authorization': client_key_value
        }
        stream_json = utils.get_webcontent(
            URL_STREAM_REPLAY % params.video_id, specific_headers=specific_headers_data)
        stream_jsonparser = json.loads(stream_json)
        return stream_jsonparser["url"]