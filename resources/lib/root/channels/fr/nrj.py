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


URL_ROOT = 'http://www.nrj-play.fr'

URL_REPLAY = URL_ROOT + '/%s/replay'
# channel_name (nrj12, ...)

URL_COMPTE_LOGIN = URL_ROOT + '/compte/login'
# TO DO add account for using Live Direct

URL_LIVE_WITH_TOKEN = URL_ROOT + '/compte/live?channel=%s'
# channel (nrj12, ...) -
# call this url after get session (url live with token inside this page)


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


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build shows listing"""
    shows = []

    if params.next == 'list_shows_1':
        categories_html = utils.get_webcontent(
            URL_REPLAY % params.channel_name)
        categories_soup = bs(categories_html, 'html.parser')
        categories = categories_soup.find(
            'ul', class_='subNav-menu hidden-xs').find_all('a')

        for category in categories:

            category_title = category.get_text().strip()
            category_url = URL_ROOT + category.get('href')

            shows.append({
                'label': category_title,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    category_url=category_url,
                    title=category_title,
                    next='list_shows_2',
                    window_title=category_title
                )
            })
    elif params.next == 'list_shows_2':
        emissions_html = utils.get_webcontent(
            params.category_url)
        emissions_soup = bs(emissions_html, 'html.parser')
        list_emissions_datas = emissions_soup.find_all(
            'div', class_='linkProgram-visual')
        
        for emission_datas in list_emissions_datas:
    
            emission_title = emission_datas.find(
                'img').get('alt')
            emission_url = URL_ROOT + emission_datas.find(
                'a').get('href')
            emission_img = ''
            if emission_datas.find('source').get('data-srcset'):
                emission_img = emission_datas.find('source').get('data-srcset')
            else:
                emission_img = emission_datas.find('source').get('srcset')

            shows.append({
                'label': emission_title,
                'thumb': emission_img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    emission_url=emission_url,
                    title=emission_title,
                    next='list_videos_1',
                    window_title=emission_title
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

    videos_html = utils.get_webcontent(
        params.emission_url)
    videos_soup = bs(videos_html, 'html.parser')
    list_videos_datas = videos_soup.find_all(
        'figure', class_='thumbnailReplay-visual')

    if len(list_videos_datas) > 0:
        
        for video_datas in list_videos_datas:
    
            video_title = params.title + ' - ' + video_datas.find(
                'img').get('alt')
            video_duration = 0
            video_url = URL_ROOT + video_datas.find('a').get('href')
            video_img = ''
            if video_datas.find('source').get('data-srcset'):
                video_img = video_datas.find('source').get('data-srcset')
            else:
                video_img = video_datas.find('source').get('srcset')
            
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
                    action='replay_entry',
                    next='play_r',
                    video_url=video_url
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })
    else:

        video_title = videos_soup.find(
            'div', class_='nrjVideo-player').find('meta').get('alt')
        video_duration = 0
        video_url = params.emission_url
        video_img = videos_soup.find(
            'div', class_='nrjVideo-player').find('meta').get('content')
        
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
    if params.next == 'play_r' or params.next == 'download_video':
        # Just One format of each video (no need of QUALITY)
        stream_html = utils.get_webcontent(
            params.video_url)
        stream_soup = bs(stream_html, 'html.parser')
        stream_datas = stream_soup.find(
            'div', class_='nrjVideo-player').find_all('meta')
        stream_url = ''
        for stream in stream_datas:
            if 'mp4' in stream.get('content'):
                stream_url = stream.get('content')
        return stream_url
    elif params.next == 'play_l':
        url_live = ''

        session_requests = requests.session()
        result = session_requests.get(URL_COMPTE_LOGIN)

        token_form_login = re.compile(
            r'name=\"login_form\[_token\]\" value=\"(.*?)\"'
        ).findall(result.text)[0]

        module_name = eval(params.module_path)[-1]

        # Build PAYLOAD
        payload = {
            "login_form[email]": common.PLUGIN.get_setting(
                module_name + '.login'),
            "login_form[password]": common.PLUGIN.get_setting(
                module_name + '.password'),
            "login_form[_token]": token_form_login
        }

        # LOGIN
        result_2 = session_requests.post(
            URL_COMPTE_LOGIN, data=payload, headers=dict(referer=URL_COMPTE_LOGIN))
        if 'adresse e-mail ou le mot de passe est invalide.' \
                in result_2.text.encode('utf-8'):
            utils.send_notification(
                params.channel_name + ' : ' + common.ADDON.get_localized_string(30711))
            return None

        # GET page with url_live with the session logged
        result_3 = session_requests.get(
            URL_LIVE_WITH_TOKEN % (params.channel_name),
            headers=dict(
                referer=URL_LIVE_WITH_TOKEN % (params.channel_name)))

        root_soup = bs(result_3.text, 'html.parser')
        live_soup = root_soup.find('div', class_="player")

        url_live_json = live_soup.get('data-options')
        url_live_json_jsonparser = json.loads(url_live_json)

        return url_live_json_jsonparser["file"]
