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
from resources.lib import common


# TO DO
#   Most recent
#   Most viewed

URL_ROOT = 'https://www.arte.tv/%s/'
# Language

URL_REPLAY_ARTE = 'https://api.arte.tv/api/player/v1/config/%s/%s'
# desired_language, videoid

URL_LIVE_ARTE = 'https://api.arte.tv/api/player/v1/livestream/%s'
# Langue, ...

URL_VIDEOS = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/v3/videos/subcategory/%s/page/%s/limit/100/%s'
# VideosCode, Page, language

URL_VIDEOS_2 = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/v3/videos/collection/%s/%s/%s'
# VideosCode, Page, language

DESIRED_LANGUAGE = common.PLUGIN.get_setting(
    'arte.language')


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
            URL_ROOT % DESIRED_LANGUAGE.lower())
        file_replay = re.compile(
            r'_INITIAL_STATE__ = (.*?);').findall(file_replay)[0]
        json_parser = json.loads(file_replay)

        value_code = json_parser['pages']['currentCode']

        for category in json_parser['pages']['list'][value_code]['zones']:

            if category['type'] == 'category':
                category_name = category['title']
                category_url = category['link']['url']

                shows.append({
                    'label': category_name,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        next='list_shows_2',
                        category_name=category_name,
                        category_url=category_url,
                        window_title=category_name
                    )
                })
    elif params.next == 'list_shows_2':
        file_replay = utils.get_webcontent(
            params.category_url)
        file_replay = re.compile(
            r'_INITIAL_STATE__ = (.*?);').findall(file_replay)[0]
        json_parser = json.loads(file_replay)

        value_code = json_parser['pages']['currentCode']

        for category in json_parser['pages']['list'][value_code]['zones']:

            sub_category_name = ''
            if category['type'] == 'category':
                sub_category_name = category['title']
                sub_category_type = category['type']
                next_value = 'list_videos_1'
                datas = category['link']['page']
            if category['type'] == 'playlist':
                sub_category_name = category['title']
                sub_category_type = category['type']
                next_value = 'list_shows_3'
                datas = params.category_url
            if category['type'] == 'collection':
                sub_category_name = category['title']
                sub_category_type = category['type']
                next_value = 'list_shows_3'
                datas = params.category_url
            if category['type'] == 'magazine':
                sub_category_name = category['title']
                sub_category_type = category['type']
                next_value = 'list_shows_3'
                datas = params.category_url

            if sub_category_name != '':
                shows.append({
                    'label': sub_category_name,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        next=next_value,
                        sub_category_name=sub_category_name,
                        datas=datas,
                        type=category['type'],
                        sub_category_type=sub_category_type,
                        page='1',
                        window_title=sub_category_name
                    )
                })

    elif params.next == 'list_shows_3':

        file_replay = utils.get_webcontent(
            params.datas)
        file_replay = re.compile(
            r'_INITIAL_STATE__ = (.*?);').findall(file_replay)[0]
        json_parser = json.loads(file_replay)

        value_code = json_parser['pages']['currentCode']

        for category in json_parser['pages']['list'][value_code]['zones']:

            if category['type'] == params.sub_category_type:
                for program_datas in category['data']:
                    program_title = program_datas['title'].encode('utf-8')
                    datas = program_datas['programId']
                    program_img = ''
                    for images in program_datas['images']['landscape']['resolutions']:
                        program_img = images['url']

                    shows.append({
                        'label': program_title,
                        'thumb': program_img,
                        'url': common.PLUGIN.get_url(
                            module_path=params.module_path,
                            module_name=params.module_name,
                            action='replay_entry',
                            next='list_videos_1',
                            datas=datas,
                            type=params.type,
                            page='1',
                            window_title=program_title
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
        
        if params.type == 'category':
            file_replay = utils.get_webcontent(
                URL_VIDEOS % (params.datas, params.page, DESIRED_LANGUAGE.lower()))
        else:
            file_replay = utils.get_webcontent(
                URL_VIDEOS_2 % (params.type.upper(), params.datas, DESIRED_LANGUAGE.lower()))
        json_parser = json.loads(file_replay)

        for video_datas in json_parser['videos']:
            
            if video_datas['subtitle'] is not None:
                title = video_datas['title'] + ' - ' + video_datas['subtitle']
            else:
                title = video_datas['title']
            video_id = video_datas['programId']
            img = video_datas['imageUrl']
            duration = video_datas["durationSeconds"]
            plot = video_datas["shortDescription"]
            info = {
                'video': {
                    'title': title,
                    'plot': plot,
                    'duration': duration,
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

        if int(json_parser['meta']['totalCount']) > int(params.page):
            # More videos...
            videos.append({
                'label': common.ADDON.get_localized_string(30700),
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next=params.next,
                    datas=params.datas,
                    page=str(int(params.page) + 1),
                    window_title=params.window_title,
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


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    if DESIRED_LANGUAGE == 'FR' or \
            DESIRED_LANGUAGE == 'DE':
        params['next'] = 'play_l'
        return get_video_url(params)
    else:
        return None


def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_r' or params.next == 'download_video':
        file_medias = utils.get_webcontent(
            URL_REPLAY_ARTE % (
                DESIRED_LANGUAGE.lower(), params.video_id))
        json_parser = json.loads(file_medias)

        url_selected = ''
        video_streams = json_parser['videoJsonPlayer']['VSR']

        desired_quality = common.PLUGIN.get_setting('quality')

        if desired_quality == "DIALOG":
            all_datas_videos_quality = []
            all_datas_videos_path = []

            for video in video_streams:
                if not video.find("HLS"):
                        datas = json_parser['videoJsonPlayer']['VSR'][video]
                        all_datas_videos_quality.append(
                            datas['mediaType'] + " (" +
                            datas['versionLibelle'] + ")")
                        all_datas_videos_path.append(datas['url'])

            seleted_item = common.sp.xbmcgui.Dialog().select(
                "Choose Stream", all_datas_videos_quality)
            if seleted_item > -1:
                url_selected = all_datas_videos_path[seleted_item].encode(
                    'utf-8')
            else:
                return None

        elif desired_quality == "BEST":
            url_selected = video_streams['HTTPS_SQ_1']['url']
            url_selected = url_selected.encode('utf-8')
        else:
            url_selected = video_streams['HTTPS_HQ_1']['url'].encode('utf-8')

        return url_selected
    elif params.next == 'play_l':
        file_live = utils.get_webcontent(
            URL_LIVE_ARTE % DESIRED_LANGUAGE.lower())
        json_parser = json.loads(file_live)
        return json_parser["videoJsonPlayer"]["VSR"]["HLS_SQ_1"]["url"]
