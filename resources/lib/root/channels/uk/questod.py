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
from resources.lib import common

# TO DO
# Live TV protected by DRM

URL_ROOT = 'https://www.questod.co.uk'

URL_SHOWS = URL_ROOT + '/api/shows/%s/?limit=12&page=%s'
# mode, page

URL_SHOWS_AZ = URL_ROOT + '/api/shows%s'
# mode

URL_VIDEOS = URL_ROOT + '/api/show-detail/%s'
# showId

URL_STREAM = URL_ROOT + '/api/video-playback/%s'
# videoId

SHOW_MODE = {
    'FEATURED': 'featured',
    'MOST POPULAR': 'most-popular',
    'NEW': 'new'
}

SHOW_MODE_AZ = {
    'A-Z': '-az'
}

def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        params.next = "list_shows_1"
        params["page"] = "1"
        return list_shows(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build shows listing"""
    shows = []
    if 'previous_listing' in params:
        shows = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_shows_1':

        for show_mode_title, show_mode_value in SHOW_MODE.iteritems():

            shows.append({
                'label': show_mode_title,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    page='1',
                    show_mode_value=show_mode_value,
                    next='list_shows_2',
                    show_title=show_mode_title,
                    window_title=show_mode_title
                )
            })

        for show_mode_title, show_mode_value in SHOW_MODE_AZ.iteritems():

            shows.append({
                'label': show_mode_title,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    page='1',
                    show_mode_value=show_mode_value,
                    next='list_shows_2_2',
                    show_title=show_mode_title,
                    window_title=show_mode_title
                )
            })

    elif params.next == 'list_shows_2':

        list_shows_json = utils.get_webcontent(
            URL_SHOWS % (params.show_mode_value, params.page))
        list_shows_jsonparser = json.loads(list_shows_json)

        for show_datas in list_shows_jsonparser["items"]:

            show_title = show_datas["title"]
            show_id = show_datas["id"]
            show_image = show_datas["image"]["src"]

            shows.append({
                'label': show_title,
                'thumb': show_image,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='list_shows_3',
                    show_id=show_id,
                    show_title=show_title,
                    window_title=show_title
                )
            })

        # More programs...
        shows.append({
            'label': common.ADDON.get_localized_string(30708),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='list_shows_1',
                page=str(int(params.page) + 1),
                show_mode_value=params.show_mode_value,
                update_listing=True,
                previous_listing=str(shows)
            )
        })

    elif params.next == 'list_shows_2_2':

        list_shows_json = utils.get_webcontent(
            URL_SHOWS_AZ % (params.show_mode_value))
        list_shows_jsonparser = json.loads(list_shows_json)


        for show_datas_letter in list_shows_jsonparser:

            for show_datas in show_datas_letter["items"]:

                show_title = show_datas["title"]
                show_id = show_datas["id"]

                shows.append({
                    'label': show_title,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        next='list_shows_3',
                        show_id=show_id,
                        show_title=show_title,
                        window_title=show_title
                    )
                })

    elif params.next == 'list_shows_3':

        list_seasons_json = utils.get_webcontent(
            URL_VIDEOS % params.show_id)
        list_seasons_jsonparser = json.loads(list_seasons_json)

        for season_datas in list_seasons_jsonparser["show"]["seasonNumbers"]:

            show_season = 'Season - ' + str(season_datas)
            show_season_id = season_datas

            shows.append({
                'label': show_season,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='list_videos_1',
                    show_season_id=show_season_id,
                    show_id=params.show_id,
                    show_season=show_season,
                    window_title=show_season
                )
            })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        update_listing='update_listing' in params,
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []

    if params.next == 'list_videos_1':
        list_videos_json = utils.get_webcontent(
            URL_VIDEOS % params.show_id)
        list_videos_jsonparser = json.loads(list_videos_json)

        if 'episode' in list_videos_jsonparser["videos"]:
            if params.show_season_id in list_videos_jsonparser["videos"]["episode"]:
                for video_datas in list_videos_jsonparser["videos"]["episode"][params.show_season_id]:

                    video_title = video_datas["title"]

                    video_duration = int(str(int(video_datas["videoDuration"])/1000))
                    video_plot = video_datas["description"]
                    video_img = video_datas["image"]["src"]
                    video_id = video_datas["id"]

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

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        content='tvshows',
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_live_item(params):
    return None


def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_r' or params.next == 'download_video':
        list_stream_json = utils.get_webcontent(
            URL_STREAM % params.video_id)
        list_stream_jsonparser = json.loads(list_stream_json)

        if 'errors' in list_stream_jsonparser:
            if list_stream_jsonparser["errors"][0]["status"] == '403':
                utils.send_notification(
                    common.ADDON.get_localized_string(30713))
            else:
                utils.send_notification(
                    common.ADDON.get_localized_string(30716))
            return None
        return list_stream_jsonparser["playback"]["streamUrlHls"]