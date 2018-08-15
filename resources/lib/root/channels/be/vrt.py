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

import json
import re
import requests
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common

# TO DO
# Find a way to get APIKey ?

# URL_JSON_LIVES = 'https://services.vrt.be/videoplayer/r/live.json'
# All lives in this JSON

URL_ROOT = 'https://www.vrt.be'

# Replay

URL_CATEGORIES_JSON = 'https://search.vrt.be/suggest?facets[categories]=%s'
# Category Name

URL_LOGIN = 'https://accounts.eu1.gigya.com/accounts.login'

URL_TOKEN = 'https://token.vrt.be'

URL_STREAM_JSON = 'https://mediazone.vrt.be/api/v1/vrtvideo/assets/%s'
# VideoID

# Live

URL_API = 'https://media-services-public.vrt.be/vualto-video-aggregator-web/rest/external/v1'

URL_TOKEN_LIVE = URL_API + '/tokens'

URL_LIVE = URL_API + '/videos/vualto_%s_geo?vrtPlayerToken=%s&client=vrtvideo'
# ChannelName

CATEGORIES_VRT = {
    '/vrtnu/a-z/': 'A-Z',
    '/vrtnu/categorieen/': 'Categorieën'
}


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
    else:
        return None


def get_api_key():
    api_key_html = utils.get_webcontent(
        URL_ROOT + '/vrtnu/')
    #return re.compile(
    #    'apiKey=(.*?)\&').findall(api_key_html)[0]
    return '3_qhEcPa5JGFROVwu5SWKqJ4mVOIkwlFNMSKwzPDAh8QZOtHqu6L4nD5Q7lk0eXOOG'


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []

    if params.next == 'list_shows_1':
        for category_context, category_title in CATEGORIES_VRT.iteritems():

            category_url = URL_ROOT + category_context

            shows.append({
                'label': category_title,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='list_shows_2',
                    page='0',
                    title=category_title,
                    category_url=category_url,
                    window_title=category_title
                )
            })

    elif params.next == 'list_shows_2':

        if 'categorieen' in params.category_url:

            categories_html = utils.get_webcontent(
                params.category_url)
            categories_soup = bs(categories_html, 'html.parser')
            list_datas = categories_soup.find_all(
                'li', class_="vrtlist__item vrtlist__item--grid")
            value_next = 'list_shows_3'

        elif 'a-z' in params.category_url:
            emissions_html = utils.get_webcontent(
                params.category_url)
            emissions_soup = bs(emissions_html, 'html.parser')
            list_datas = emissions_soup.find_all(
                'li', class_="vrtlist__item vrtglossary__item")
            value_next = 'list_videos_1'

        for data in list_datas:

            data_url = URL_ROOT + data.find('a').get('href')
            data_img = 'https:' + data.find(
                'img').get('srcset').split('1x')[0].strip()
            if data.find('p'):
                data_title = data.find(
                    'h3').get_text().encode('utf-8') + ' - ' + \
                    data.find('p').get_text().encode('utf-8')
            else:
                data_title = data.find(
                    'h3').get_text().encode('utf-8')

            shows.append({
                'label': data_title,
                'thumb': data_img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    data_title=data_title,
                    action='replay_entry',
                    data_url=data_url,
                    next=value_next,
                    window_title=data_title
                )
            })

    elif params.next == 'list_shows_3':

        category_name = re.compile(
            'categorieen/(.*?)/').findall(params.data_url)[0]
        emissions_json = utils.get_webcontent(
            URL_CATEGORIES_JSON % category_name)
        emissions_jsonparser = json.loads(emissions_json)

        for data in emissions_jsonparser:

            data_url = 'https:' + data['targetUrl']
            data_img = 'https:' + data['thumbnail']
            data_title = data['title']

            shows.append({
                'label': data_title,
                'thumb': data_img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    data_title=data_title,
                    action='replay_entry',
                    data_url=data_url,
                    next='list_videos_1',
                    window_title=data_title
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

    if params.next == 'list_videos_1':
        file_path = utils.get_webcontent(params.data_url)
        episodes_soup = bs(file_path, 'html.parser')

        if episodes_soup.find('ul', class_='swiper-wrapper'):
            list_episodes = episodes_soup.find(
                'ul', class_='swiper-wrapper').find_all('li')

            for episode in list_episodes:

                title = episode.find('h3').get_text().strip()
                duration = 0
                video_url = URL_ROOT + episode.find('a').get('href')
                img = 'https:' + episode.find(
                    'img').get('srcset').split('1x')[0].strip()

                info = {
                    'video': {
                        'title': title,
                        # 'plot': plot,
                        # 'episode': episode_number,
                        # 'season': season_number,
                        # 'rating': note,
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
                    'fanart': img,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        next='play_r',
                        video_url=video_url
                    ),
                    'is_playable': True,
                    'info': info,
                    'context_menu': context_menu
                })
        else:
            if episodes_soup.find(
                'div', class_='content-container'):
                episode = episodes_soup.find(
                    'div', class_='content-container')

                title = episode.find(
                    'span', class_='content__title').get_text().strip()
                plot = episode.find(
                    'span', class_='content__shortdescription').get_text(
                    ).strip()
                duration = 0
                video_url = re.compile(
                    r'page_url":"(.*?)"').findall(file_path)[0]
                img = 'https:' + episode.find(
                    'img').get('srcset').strip()

                info = {
                    'video': {
                        'title': title,
                        'plot': plot,
                        # 'episode': episode_number,
                        # 'season': season_number,
                        # 'rating': note,
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
                    'fanart': img,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
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
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_DATE
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
        token_json = utils.get_webcontent(
            URL_TOKEN_LIVE, request_type='post')
        token_jsonparser = json.loads(token_json)
        url_stream_json = utils.get_webcontent(
            URL_LIVE % (params.channel_name, token_jsonparser["vrtPlayerToken"]))
        url_stream_jsonparser = json.loads(url_stream_json)
        url_live = ''
        if "code" in url_stream_jsonparser:
            if url_stream_jsonparser["code"] == "INVALID_LOCATION":
                utils.send_notification(
                    common.ADDON.get_localized_string(30713))
            return None
        for url_stream_datas in url_stream_jsonparser["targetUrls"]:
            if url_stream_datas["type"] == "hls_aes":
                url_live = url_stream_datas["url"]
        return url_live
    elif params.next == 'play_r' or params.next == 'download_video':

        session_requests = requests.session()

        module_name = eval(params.module_path)[-1]

        # Build PAYLOAD
        payload = {
            'loginID': common.PLUGIN.get_setting(
                module_name + '.login'),
            'password': common.PLUGIN.get_setting(
                module_name + '.password'),
            'targetEnv': 'jssdk',
            'APIKey': get_api_key(),
            'includeSSOToken': 'true',
            'authMode': 'cookie'
        }
        result = session_requests.post(
            URL_LOGIN,
            data = payload)
        result_jsonpaser = json.loads(result.text)
        if result_jsonpaser['statusCode'] != 200:
            utils.send_notification(
                params.channel_name + ' : ' + common.ADDON.get_localized_string(30711))
            return None

        headers = {'Content-Type': 'application/json',
            'Referer': URL_ROOT + '/vrtnu/'}
        data = '{"uid": "%s", ' \
            '"uidsig": "%s", ' \
            '"ts": "%s", ' \
            '"email": "%s"}' % (
            result_jsonpaser['UID'],
            result_jsonpaser['UIDSignature'],
            result_jsonpaser['signatureTimestamp'],
            common.PLUGIN.get_setting(
                module_name + '.login'))
        result_2 = session_requests.post(
            URL_TOKEN,
            data=data,
            headers=headers)

        build_url = params.video_url[:-1] + '.mssecurevideo.json'
        result_3 = session_requests.get(build_url)
        video_id_json = json.loads(result_3.text)
        video_id = ''
        for key in video_id_json.iteritems():
            video_id = video_id_json[key[0]]['videoid']

        result_4 = session_requests.get(
            URL_STREAM_JSON % video_id)
        streams_json = json.loads(result_4.text)
        url = ''
        for stream in streams_json['targetUrls']:
            if 'HLS' in stream['type']:
                url = stream['url']
        return url
