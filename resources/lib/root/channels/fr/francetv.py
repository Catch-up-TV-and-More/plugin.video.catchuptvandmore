# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Original work (C) JUL1EN094, SPM, SylvainCecchetto
    Copyright (C) 2016  SylvainCecchetto

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
import time
from resources.lib import utils
from resources.lib import common


'''
Channels:
    * France 2
    * France 3 Nationale
    * France 4
    * France Ô
    * France 5
'''

URL_API = 'http://api-front.yatta.francetv.fr'

URL_LIVE_JSON = URL_API + '/standard/edito/directs'

URL_LAST_VIDEOS = URL_API + '/standard/publish/channels/%s/contents'
# channel_name

SHOW_INFO = 'http://sivideo.webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion=%s'
# VideoId

URL_CATEGORIES = URL_API + '/standard/publish/channels/%s/categories'
# channel_name

URL_PROGRAMS = URL_API + '/standard/publish/categories/%s/programs/%s'
# category, channel_name

HDFAUTH_URL = 'http://hdfauth.francetv.fr/esi/TA?format=json&url=%s'


URL_SEARCH_VIDEOS = 'https://vwdlashufe-dsn.algolia.net/1/indexes/' \
                    'yatta_prod_contents/query'

URL_YATTA_VIDEO = URL_API + '/standard/publish/contents/%s'
# Param : id_yatta

URL_VIDEOS = URL_API + '/standard/publish/taxonomies/%s/contents'
# program

HEADERS_YATTA = {
    'X-Algolia-API-Key': '80d9c91958fc448dd20042d399ebdf16',
    'X-Algolia-Application-Id': 'VWDLASHUFE'
}


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
    elif 'search' in params.next:
        return search(params)
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

    if params.next == 'list_shows_root':

        json_filepath = utils.download_catalog(
            URL_CATEGORIES % (params.channel_name),
            '%s.json' % (params.channel_name)
        )
        with open(json_filepath) as json_file:
            json_parser = json.load(json_file)

        for categories in json_parser["result"]:

            categories_name = categories["label"].encode('UTF-8')
            categories_part_url = categories["url"]
            shows.append({
                'label': categories_name,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    categories_part_url=categories_part_url,
                    next='list_shows_2_cat',
                    window_title=categories_name
                )
            })

        # Last videos
        shows.append({
            'label': common.GETTEXT('Last videos'),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='list_videos_2',
                page='0',
                window_title=common.GETTEXT('Last videos')
            )
        })

        # Search videos
        shows.append({
            'label': common.GETTEXT('Search videos'),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='search',
                window_title=common.GETTEXT('Search videos'),
                is_folder=False
            )
        })

    elif params.next == 'list_shows_2_cat':
        
        json_filepath = utils.download_catalog(
            URL_PROGRAMS % (params.categories_part_url, params.channel_name),
            '%s_%s.json' % (params.categories_part_url, params.channel_name),
            params={'filter': 'with-no-vod,only-visible'}
        )
        with open(json_filepath) as json_file:
            json_parser = json.load(json_file)

        for program in json_parser["result"]:

            program_name = program["label"].encode('UTF-8')
            program_img = ''

            if 'media_image' in program:
                if program["media_image"] is not None:
                    for image_datas in program["media_image"]["patterns"]:
                        if "vignette_16x9" in image_datas["type"]:
                            program_img = URL_API + image_datas["urls"]["w:1024"]
            program_part_url = program["url_complete"].replace('/', '_')
            shows.append({
                'label': program_name,
                'thumb': program_img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    program_part_url=program_part_url,
                    next='list_videos_1',
                    page='0',
                    window_title=program_name
                )
            })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
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

    if 'search' in params.next:
        url_search = URL_SEARCH_VIDEOS
        body = "{\"params\": \"filters=class:video&page=%s&query=%s\"}" % (
            params.page, params.query)

        result = utils.get_webcontent(
            url_search,
            request_type='post',
            specific_headers=HEADERS_YATTA,
            post_dic=body
        )

        json_d = json.loads(result)
        nb_pages = json_d['nbPages']
        for hit in json_d['hits']:
            label = hit['program']['label']
            title = hit['title']
            headline = hit['headline_title']
            desc = hit['text']
            duration = hit['duration']
            season = hit['season_number']
            episode = hit['episode_number']
            id_yatta = hit['id']
            director = hit['director']
            # producer = hit['producer']
            presenter = hit['presenter']
            casting = hit['casting']
            # characters = hit['characters']
            last_publication_date = hit['dates']['last_publication_date']
            image_400 = ''
            image_1024 = ''
            if 'image' in hit: 
                image_400 = hit['image']['formats']['vignette_16x9']['urls']['w:400']
                image_1024 = hit['image']['formats']['vignette_16x9']['urls']['w:1024']

            image_400 = URL_API + image_400
            image_1024 = URL_API + image_1024

            title = label + ' - ' + title
            if headline and headline != '':
                desc = headline + '\n' + desc

            if not director:
                director = presenter

            info = {
                'video': {
                    'title': title,
                    'plot': desc,
                    'aired': time.strftime(
                        '%Y-%m-%d', time.localtime(last_publication_date)),
                    'date': time.strftime(
                        '%d.%m.%Y', time.localtime(last_publication_date)),
                    'duration': duration,
                    'year': time.strftime(
                        '%Y', time.localtime(last_publication_date)),
                    'mediatype': 'tvshow',
                    'season': season,
                    'episode': episode,
                    'cast': casting.split(', '),
                    'director': director
                }
            }

            download_video = (
                common.GETTEXT('Download'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='download_video',
                    module_path=params.module_path,
                    module_name=params.module_name,
                    id_yatta=id_yatta) + ')'
            )
            context_menu = []
            context_menu.append(download_video)

            videos.append({
                'label': title,
                'fanart': image_1024,
                'thumb': image_400,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='play_r',
                    id_yatta=id_yatta
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu,
                # 'subtitles': 'subtitles'
            })

        if int(params.page) != nb_pages - 1:
            # More videos...
            videos.append({
                'label': common.ADDON.get_localized_string(30700),
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next=params.next,
                    query=params.query,
                    page=str(int(params.page) + 1),
                    window_title=params.window_title,
                    update_listing=True,
                    previous_listing=str(videos)
                )
            })

        return common.PLUGIN.create_listing(
            videos,
            sort_methods=(
                common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
                common.sp.xbmcplugin.SORT_METHOD_DATE,
                common.sp.xbmcplugin.SORT_METHOD_DURATION,
                common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
                common.sp.xbmcplugin.SORT_METHOD_EPISODE

            ),
            content='tvshows',
            update_listing='update_listing' in params,
            category=common.get_window_title(params)
        )

    else:
        
        if params.next == 'list_videos_1':
            json_filepath = utils.download_catalog(
                URL_VIDEOS % params.program_part_url,
                '%s_%s.json' % (params.program_part_url, params.page),
                params={'page': params.page, 'filter': 'with-no-vod,only-visible'}
            )
            with open(json_filepath) as json_file:
                json_parser = json.load(json_file)
        elif params.next == 'list_videos_2':
            json_filepath = utils.download_catalog(
                URL_LAST_VIDEOS % params.channel_name,
                '%s_%s.json' % (params.channel_name, params.page),
                params={'page': params.page, 'filter': 'with-no-vod,only-visible'}
            )
            with open(json_filepath) as json_file:
                json_parser = json.load(json_file)

        for video_datas in json_parser["result"]:
            
            if video_datas["type"] == 'extrait':
                title = video_datas["type"].encode('UTF-8') + ' - ' + video_datas["title"].encode('UTF-8')
            else:
                title = video_datas["title"].encode('UTF-8')

            id_diffusion = ''
            duration = 0
            image = ''
            for video_media in video_datas["content_has_medias"]:
                if "main" in video_media["type"]:
                    id_diffusion = video_media["media"]["si_id"]
                    if video_datas["type"] != 'extrait':
                        duration = int(video_media["media"]["duration"])
                elif "image" in video_media["type"]:
                    for image_datas in video_media["media"]["patterns"]:
                        if "vignette_16x9" in image_datas["type"]:
                            image = URL_API + image_datas["urls"]["w:1024"]
            
            date_value = video_datas["creation_date"].split('T')[0].split('-')
            year = int(date_value[0])
            day = date_value[2]
            month = date_value[1]
            date = '.'.join((day, month, str(year)))
            aired = '-'.join((str(year), month, day))

            plot = ''
            if "text" in video_datas:
                plot = video_datas["text"]

            info = {
                'video': {
                    'title': title,
                    'duration': duration,
                    'plot': plot,
                    'aired': aired,
                    'date': date,
                    'year': year
                }
            }

            download_video = (
            common.GETTEXT('Download'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='download_video',
                    module_path=params.module_path,
                    module_name=params.module_name,
                    id_diffusion=id_diffusion) + ')'
                )
            context_menu = []
            context_menu.append(download_video)

            videos.append({
                'label': title,
                'fanart': image,
                'thumb': image,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='play_r',
                    id_diffusion=id_diffusion
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

        if json_parser["cursor"]["next"] is not None:
            # More videos...
            videos.append({
                'label': common.ADDON.get_localized_string(30700),
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next=params.next,
                    program_part_url=params.program_part_url,
                    page=str(json_parser["cursor"]["next"]),
                    window_title=params.window_title,
                    update_listing=True,
                    previous_listing=str(videos)
                )
            })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_DATE,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
            common.sp.xbmcplugin.SORT_METHOD_EPISODE

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

    desired_quality = common.PLUGIN.get_setting('quality')

    if params.next == 'play_r' or params.next == 'download_video':
        if 'id_yatta' in params:
            result = utils.get_webcontent(URL_YATTA_VIDEO % params.id_yatta)
            result = json.loads(result)
            for media in result['content_has_medias']:
                if 'si_id' in media['media']:
                    params['id_diffusion'] = media['media']['si_id']
                    break

        json_parser = json.loads(
            utils.get_webcontent(SHOW_INFO % (params.id_diffusion)))
        
        subtitles = []
        if json_parser['subtitles']:
            subtitles_list = json_parser['subtitles']
            for subtitle in subtitles_list:
                if subtitle['format'] == 'vtt':
                    subtitles.append(
                        subtitle['url'].encode('utf-8'))

        url_selected = ''

        if desired_quality == "DIALOG":
            all_datas_videos_quality = []
            all_datas_videos_path = []

            for video in json_parser['videos']:
                if video['format'] == 'hls_v5_os' or \
                        video['format'] == 'm3u8-download':
                    if video['format'] == 'hls_v5_os':
                        all_datas_videos_quality.append("HD")
                    else:
                        all_datas_videos_quality.append("SD")
                    all_datas_videos_path.append(
                        (video['url'], video['drm']))

            seleted_item = common.sp.xbmcgui.Dialog().select(
                common.GETTEXT('Choose video quality'),
                all_datas_videos_quality)

            if seleted_item == -1:
                return None

            url_selected = all_datas_videos_path[seleted_item][0]
            drm = all_datas_videos_path[seleted_item][1]

        elif desired_quality == "BEST":
            for video in json_parser['videos']:
                if video['format'] == 'hls_v5_os':
                    url_selected = video['url']
                    drm = video['drm']
        else:
            for video in json_parser['videos']:
                if video['format'] == 'm3u8-download':
                    url_selected = video['url']
                    drm = video['drm']

        if drm:
            utils.send_notification(
                common.ADDON.get_localized_string(30702))
            return None
        else:
            return url_selected

    elif params.next == 'play_l':

        json_parser = json.loads(utils.get_webcontent(
            URL_LIVE_JSON))
        for live in json_parser["result"]:
            if live["channel"] == params.channel_name:
                live_datas = live["collection"][0]["content_has_medias"]
                liveId = ''
                for live_data in live_datas:
                    if "si_direct_id" in live_data["media"]:
                        liveId = live_data["media"]["si_direct_id"]
                json_parser_liveId = json.loads(utils.get_webcontent(
                    SHOW_INFO % liveId))
                url_hls_v1 = ''
                url_hls_v5 = ''
                url_hls = ''

                for video in json_parser_liveId['videos']:
                    if 'format' in video:
                        if 'hls_v1_os' in video['format'] and \
                                video['geoblocage'] is not None:
                            url_hls_v1 = video['url']
                        if 'hls_v5_os' in video['format'] and \
                                video['geoblocage'] is not None:
                            url_hls_v5 = video['url']
                        if 'hls' in video['format']:
                            url_hls = video['url']

                final_url = ''

                # Case France 3 Région
                if url_hls_v1 == '' and url_hls_v5 == '':
                    final_url = url_hls
                # Case Jarvis
                if common.sp.xbmc.__version__ == '2.24.0' \
                        and url_hls_v1 != '':
                    final_url = url_hls_v1
                # Case Krypton, Leia, ...
                if final_url == '' and url_hls_v5 != '':
                    final_url = url_hls_v5
                elif final_url == '':
                    final_url = url_hls_v1

                json_parser2 = json.loads(
                    utils.get_webcontent(HDFAUTH_URL % (final_url)))

                return json_parser2['url']


def search(params):
    keyboard = common.sp.xbmc.Keyboard(
        default='',
        title='',
        hidden=False)
    keyboard.doModal()
    if keyboard.isConfirmed():
        query = keyboard.getText()
        params['page'] = '0'
        params['query'] = query
        params['next'] = 'list_videos_search'
        return list_videos(params)
    else:
        return None
