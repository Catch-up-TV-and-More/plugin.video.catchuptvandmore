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
import base64
import json
import re
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common

# TO DO
# Add info Video (duration, ...)

URL_ROOT = 'https://www.channelnewsasia.com'

URL_LIVE_ID = URL_ROOT + '/news/livetv'

URL_VIDEO_VOD = 'https://player.ooyala.com/sas/player_api/v2/authorization/' \
                'embed_code/%s/%s?device=html5&domain=www.channelnewsasia.com'
# pcode, liveId

URL_GET_JS_PCODE = URL_ROOT + '/blueprint/cna/js/main.js'

URL_VIDEOS_DATAS = URL_ROOT + '/news/videos'

URL_VIDEOS = URL_ROOT + '/dynamiclist?channelId=%s&contextId=%s&pageIndex=%s'
# showId, contextId, page

URL_SHOWS_DATAS = URL_ROOT + '/news/video-on-demand'

URL_SHOWS = URL_ROOT + '/dynamiclist?contextId=%s&pageIndex=%s'

def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
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
    params['next'] = 'list_shows_root'
    params['module_name'] = params.module_name
    params['module_path'] = params.module_path
    return channel_entry(params)

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []
    if 'previous_listing' in params:
        shows = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_shows_root':
        show_title = 'Videos'
        shows.append({
            'label': show_title,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                title=show_title,
                next='list_shows_videos_1',
                window_title=show_title
            )
        })

        show_title = 'Video On Demand'
        shows.append({
            'label': show_title,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                title=show_title,
                page='1',
                next='list_shows_video_on_demand_1',
                window_title=show_title
            )
        })

    elif params.next == 'list_shows_videos_1':
        videos_categories_html = utils.get_webcontent(
            URL_VIDEOS_DATAS)
        context_id = re.compile(
            'contextId\" value=\"(.*?)\"').findall(videos_categories_html)[0]
        videos_categories_soup = bs(videos_categories_html, 'html.parser')
        videos_categories_list = videos_categories_soup.find(
            'select', class_="filter__input i-arrow-select-small-red").find_all('option')
        for videos_category in videos_categories_list:
            show_title = videos_category.get('label')
            show_id = videos_category.get('value')

            shows.append({
                'label': show_title,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    title=show_title,
                    show_id=show_id,
                    page='1',
                    context_id=context_id,
                    next='list_videos_videos_1',
                    window_title=show_title
                )
            })         

    elif params.next == 'list_shows_video_on_demand_1':
        shows_datas_html = utils.get_webcontent(
            URL_SHOWS_DATAS)
        context_id = re.compile(
            'contextId\" value=\"(.*?)\"').findall(shows_datas_html)[0]
        shows_datas_json = utils.get_webcontent(
            URL_SHOWS % (context_id, params.page))
        shows_datas_jsonparser = json.loads(shows_datas_json)
        for show_data in shows_datas_jsonparser["items"]:
            show_title = show_data["title"]
            show_img = ''
            for img_datas in show_data["image"]["items"][0]["srcset"]:  
                show_img = URL_ROOT + img_datas["src"]
            show_url = URL_ROOT + show_data["url"]

            shows.append({
                'label': show_title,
                'thumb': show_img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    title=show_title,
                    show_url=show_url,
                    page='1',
                    next='list_videos_on_demand_videos_1',
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
                next=params.next,
                page=str(int(params.page) + 1),
                update_listing=True,
                previous_listing=str(shows)
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
    if 'previous_listing' in params:
        videos = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_videos_videos_1':

        videos_datas_json = utils.get_webcontent(
            URL_VIDEOS % (params.show_id, params.context_id, params.page))
        videos_datas_jsonparser = json.loads(videos_datas_json)

        for video_datas in videos_datas_jsonparser['items']:
            title = video_datas["image"]["alt"].replace(' | Video', '')
            img = video_datas["image"]["src"]
            url = URL_ROOT + video_datas["url"]

            info = {
                'video': {
                    'title': title,
                    # 'aired': aired,
                    # 'date': date,
                    # 'duration': video_duration,
                    # 'year': year,
                    # 'plot': plot,
                    'mediatype': 'tvshow'
                }
            }

            download_video = (
                common.GETTEXT('Download'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='download_video',
                    module_path=params.module_path,
                    module_name=params.module_name,
                    url=url) + ')'
            )
            context_menu = []
            context_menu.append(download_video)

            videos.append({
                'label': title,
                'thumb': img,
                'fanart': img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                     module_name=params.module_name,
                    action='replay_entry',
                    next='play_r',
                    url=url
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

        # More videos...
        videos.append({
            'label': common.ADDON.get_localized_string(30700),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next=params.next,
                page=str(int(params.page) + 1),
                show_id=params.show_id,
                context_id=params.context_id,
                title=params.title,
                window_title=params.window_title,
                update_listing=True,
                previous_listing=str(videos)
            )
        })
    
    elif params.next == 'list_videos_on_demand_videos_1':
        
        shows_datas_html = utils.get_webcontent(
            params.show_url)
        context_id = re.compile(
            'contextId\" value=\"(.*?)\"').findall(shows_datas_html)[0]
        videos_datas_json = utils.get_webcontent(
            URL_SHOWS % (context_id, params.page))
        videos_datas_jsonparser = json.loads(videos_datas_json)

        for video_datas in videos_datas_jsonparser['items']:
            title = video_datas["title"]
            img = ''
            if 'src' in  video_datas["image"]:
                img = video_datas["image"]["src"]
            else:
                for img_datas in video_datas["image"]["items"][0]["srcset"]:
                    img = URL_ROOT + img_datas["src"]
            url = URL_ROOT + video_datas["url"]

            info = {
                'video': {
                    'title': title,
                    # 'aired': aired,
                    # 'date': date,
                    # 'duration': video_duration,
                    # 'year': year,
                    # 'plot': plot,
                    'mediatype': 'tvshow'
                }
            }

            download_video = (
                common.GETTEXT('Download'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='download_video',
                    module_path=params.module_path,
                    module_name=params.module_name,
                    url=url) + ')'
            )
            context_menu = []
            context_menu.append(download_video)

            videos.append({
                'label': title,
                'thumb': img,
                'fanart': img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                     module_name=params.module_name,
                    action='replay_entry',
                    next='play_r',
                    url=url
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

        # More videos...
        videos.append({
            'label': common.ADDON.get_localized_string(30700),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next=params.next,
                page=str(int(params.page) + 1),
                show_url=params.show_url,
                title=params.title,
                window_title=params.window_title,
                update_listing=True,
                previous_listing=str(videos)
            )
        })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE
        ),
        content='tvshows',
        update_listing='update_listing' in params,
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)


def get_video_url(params):
    """Get video URL and start video player"""
    stream_html = ''
    if params.next == 'play_l':
        stream_html = utils.get_webcontent(
            URL_LIVE_ID)
    elif params.next == 'play_r' or params.next == 'download':
        stream_html = utils.get_webcontent(
            params.url)
    stream_id_list = re.compile(
        'video-asset-id="(.*?)"').findall(stream_html)
    if len(stream_id_list) > 0:
        stream_pcode = utils.get_webcontent(
            URL_GET_JS_PCODE)
        pcode = re.compile(
            'ooyalaPCode\:"(.*?)"').findall(stream_pcode)[0]
        stream_json = utils.get_webcontent(
            URL_VIDEO_VOD % (pcode, stream_id_list[0]))
        stream_jsonparser = json.loads(stream_json)
        # Get Value url encodebase64
        if 'streams' in stream_jsonparser["authorization_data"][stream_id_list[0]]:
            for stream in stream_jsonparser["authorization_data"][stream_id_list[0]]["streams"]:
                if stream["delivery_type"] == 'hls':
                    url_base64 = stream["url"]["data"]
            return base64.standard_b64decode(url_base64)
        else:
            # TODO catch the error (geo-blocked, deleted, etc ...)
            utils.send_notification(
                common.ADDON.get_localized_string(30716))
    return None