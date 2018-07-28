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

import re
import json
import time
from resources.lib import utils
from resources.lib import common
from bs4 import BeautifulSoup as bs

# TO DO
# Info DATE

URL_ROOT = 'https://www.bvn.tv'

# LIVE :
URL_LIVE_DATAS = URL_ROOT + '/wp-content/themes/bvn/assets/js/app.js'
# Get Id
JSON_LIVE = 'https://json.dacast.com/b/%s/%s/%s'
# Id in 3 part
JSON_LIVE_TOKEN = 'https://services.dacast.com/token/i/b/%s/%s/%s'
# Id in 3 part

# REPLAY :
URL_TOKEN = 'https://ida.omroep.nl/app.php/auth'
URL_DAYS = URL_ROOT + '/uitzendinggemist/'
URL_INFO_REPLAY = 'https://e.omroep.nl/metadata/%s'
# Id Video, time
URL_VIDEO_REPLAY = 'https://ida.omroep.nl/app.php/%s?adaptive=yes&token=%s'
# Id Video, Token


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
    """Build categories listing"""
    shows = []

    if params.next == 'list_shows_1':
        programs_html = utils.get_webcontent(URL_DAYS)
        programs_soup = bs(programs_html, 'html.parser')
        list_days_datas = programs_soup.find_all(
            "h3", class_=re.compile("m-section__title"))
        day_id = 0

        for day_datas in list_days_datas:
            day_name = day_datas.text
            day_id = day_id + 1

            shows.append({
                'label': day_name,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='list_videos_cat',
                    day_id=day_id,
                    window_title=day_name,
                    day_name=day_name,
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

    episodes_html = utils.get_webcontent(URL_DAYS)
    episodes_soup = bs(episodes_html, 'html.parser')
    value_id = 'slick-missed-day-%s' % (params.day_id)
    shows_soup = episodes_soup.find_all(id=value_id)[0]

    for episode in shows_soup.find_all('li'):
        id_episode_list = episode.find('a').get('href').encode('utf-8').rsplit('/')
        id_episode = id_episode_list[len(id_episode_list)-1]

        title = ''
        if episode.find('span', class_="m-section__scroll__item__bottom__title--sub").text != '':
            title = episode.find('span', class_="m-section__scroll__item__bottom__title").text + \
                ' - ' + episode.find('span', class_="m-section__scroll__item__bottom__title--sub").text
        else:
            title = episode.find('span', class_="m-section__scroll__item__bottom__title").text
        img = URL_ROOT + episode.find('img').get('data-src')

        # TODO Get DATE

        info = {
            'video': {
                'title': title,
                # 'plot': plot,
                # 'episode': episode_number,
                # 'season': season_number,
                # 'rating': note,
                # 'aired': aired,
                # 'date': date,
                # 'duration': duration,
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
                id_episode=id_episode) + ')'
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
                id_episode=id_episode
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
        file_path = utils.download_catalog(
            URL_LIVE_DATAS,
            '%s_live.html' % (params.channel_name))
        live_html = open(file_path).read()
        id_value = re.compile(
            r'dacast\(\'(.*?)\'\,').findall(live_html)[0].split('_')

        # json with hls
        file_path_json = utils.download_catalog(
            JSON_LIVE % (id_value[0], id_value[1], id_value[2]),
            '%s_live.json' % (params.channel_name))
        live_json = open(file_path_json).read()
        live_jsonparser = json.loads(live_json)

        # json with token
        file_path_json_token = utils.download_catalog(
            JSON_LIVE_TOKEN % (id_value[0], id_value[1], id_value[2]),
            '%s_live_token.json' % (params.channel_name))
        live_json_token = open(file_path_json_token).read()
        live_jsonparser_token = json.loads(live_json_token)

        return 'http:' + live_jsonparser["hls"].encode('utf-8') + \
            live_jsonparser_token["token"].encode('utf-8')
    elif params.next == 'play_r' or params.next == 'download_video':
        # get token
        file_path_json_token = utils.download_catalog(
            URL_TOKEN,
            '%s_replay_token.json' % (params.channel_name))
        replay_json_token = open(file_path_json_token).read()

        replay_jsonparser_token = json.loads(replay_json_token)
        token = replay_jsonparser_token["token"]

        # Get HLS link
        file_path_video_replay = utils.download_catalog(
            URL_VIDEO_REPLAY % (params.id_episode, token),
            '%s_%s_video_replay.js' % (params.channel_name, params.id_episode))
        video_replay_json = open(file_path_video_replay).read()

        video_replay_jsonparser = json.loads(video_replay_json)
        url_hls = ''
        if 'items' in video_replay_jsonparser:
            for video in video_replay_jsonparser["items"][0]:
                url_json_url_hls = video["url"].encode('utf-8')
                break

            file_path_hls_replay = utils.download_catalog(
                url_json_url_hls + \
                'jsonpCallback%s5910' % (str(time.time()).replace('.', '')),
                '%s_%s_hls_replay.js' % (params.channel_name, params.id_episode))
            hls_replay_js = open(file_path_hls_replay).read()
            hls_replay_json = re.compile(r'\((.*?)\)').findall(hls_replay_js)[0]
            hls_replay_jsonparser = json.loads(hls_replay_json)

            if 'url' in hls_replay_jsonparser:
                url_hls = hls_replay_jsonparser["url"].encode('utf-8')
        return url_hls
