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

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

URL_JSON_LIVES = 'https://services.vrt.be/videoplayer/r/live.json'
# All lives in this JSON

URL_ROOT = 'https://www.vrt.be'

URL_CATEGORIES_JSON = 'https://search.vrt.be/suggest?facets[categories]=%s'
# Category Name

URL_LOGIN = 'https://accounts.eu1.gigya.com/accounts.login'

URL_TOKEN = 'https://token.vrt.be'

URL_STREAM_JSON = 'https://mediazone.vrt.be/api/v1/vrtvideo/assets/%s'
# VideoID

CATEGORIES_VRT = {
    '/vrtnu/a-z/': 'A-Z',
    '/vrtnu/categorieen/': 'Categorieën'
}

def channel_entry(params):
    """Entry function of the module"""
    if 'root' in params.next:
        return root(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'live' in params.next:
        return list_live(params)
    elif 'play' in params.next:
        return get_video_url(params)
    else:
        return None

def get_api_key():
    api_key_html = utils.get_webcontent(
        URL_ROOT + '/vrtnu/')
    return re.compile(
        'apiKey=(.*?)\&').findall(api_key_html)[0]

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def root(params):
    """Add Replay and Live in the listing"""
    modes = []

    # Add Replay
    modes.append({
        'label': 'Replay',
        'url': common.PLUGIN.get_url(
            action='channel_entry',
            next='list_shows_1',
            category='%s Replay' % params.channel_name.upper(),
            window_title='%s Replay' % params.channel_name
        )
    })

    # Add Live
    modes.append({
        'label' : _('Live TV'),
        'url': common.PLUGIN.get_url(
            action='channel_entry',
            next='live_cat',
            category='%s Live TV' % params.channel_name.upper(),
            window_title='%s Live TV' % params.channel_name.upper()
        ),
    })

    return common.PLUGIN.create_listing(
        modes,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title()
    )

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
                    action='channel_entry',
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
                    data_title=data_title,
                    action='channel_entry',
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
                    data_title=data_title,
                    action='channel_entry',
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
        category=common.get_window_title()
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
                    _('Download'),
                    'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                        action='download_video',
                        video_url=video_url) + ')'
                )
                context_menu = []
                context_menu.append(download_video)

                videos.append({
                    'label': title,
                    'thumb': img,
                    'fanart': img,
                    'url': common.PLUGIN.get_url(
                        action='channel_entry',
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
                video_url_json = episode.find(
                    'div', class_='vrtvideo videoplayer').get(
                    'data-analytics')
                video_url_jsonparser = json.loads(video_url_json)
                video_url = 'https:' + video_url_jsonparser['playlist']
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
                    _('Download'),
                    'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                        action='download_video',
                        video_url=video_url) + ')'
                )
                context_menu = []
                context_menu.append(download_video)

                videos.append({
                    'label': title,
                    'thumb': img,
                    'fanart': img,
                    'url': common.PLUGIN.get_url(
                        action='channel_entry',
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
        category=common.get_window_title()
    )

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_live(params):
    """Build live listing"""
    lives = []

    title = ''
    plot = ''
    duration = 0
    img = ''
    url_live = ''

    file_path = utils.download_catalog(
        URL_JSON_LIVES,
        '%s_live.json' % (params.channel_name))
    lives_json = open(file_path).read()
    lives_json = lives_json.replace(
        ')','').replace('parseLiveJson(','')
    lives_jsonparser = json.loads(lives_json)

    for lives_value in lives_jsonparser.iteritems():

        title = str(lives_value[0]).replace(
            'vualto_','').replace('_', ' ')
        url_live = lives_jsonparser[lives_value[0]]["hls"]

        info = {
            'video': {
                'title': title,
                'plot': plot,
                'duration': duration
            }
        }

        lives.append({
            'label': title,
            'fanart': img,
            'thumb': img,
            'url' : common.PLUGIN.get_url(
                action='channel_entry',
                next='play_l',
                url_live=url_live,
            ),
            'is_playable': True,
            'info': info
        })

    return common.PLUGIN.create_listing(
        lives,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_LABEL,
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        category=common.get_window_title()
    )

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_l':
        return params.url_live
    elif params.next == 'play_r' or params.next == 'download_video':

        session_requests = requests.session()

        # Build PAYLOAD
        payload = {
            'loginID': common.PLUGIN.get_setting(
                params.channel_id.rsplit('.', 1)[0] + '.login'),
            'password': common.PLUGIN.get_setting(
                params.channel_id.rsplit('.', 1)[0] + '.password'),
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
                common.ADDON.get_localized_string(30113))
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
                params.channel_id.rsplit('.', 1)[0] + '.login'))
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
