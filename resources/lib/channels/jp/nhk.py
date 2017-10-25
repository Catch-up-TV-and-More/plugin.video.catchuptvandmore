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
import base64
import json
import time
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

URL_ROOT = 'http://www3.nhk.or.jp/'

URL_ROOT_2 = 'http://www.nhk.or.jp'

URL_LIVE_NHK = 'http://www3.nhk.or.jp/%s/app/tv/hlslive_tv.xml'
# Channel_Name...

URL_COMMONJS_NHK = 'http://www3.nhk.or.jp/%s/common/js/common.js'
# Channel_Name...

URL_LIVE_INFO_NHK = 'https://api.nhk.or.jp/%s/epg/v6/%s/now.json?apikey=%s'
# Channel_Name, location, apikey ...

URL_CATEGORIES_NHK = 'https://api.nhk.or.jp/%s/vodcatlist/v2/notzero/list.json?apikey=%s'
# Channel_Name, apikey

URL_ALL_VOD_NHK = 'https://api.nhk.or.jp/%s/vodesdlist/v1/all/all/all.json?apikey=%s'
# Channel_Name, apikey

URL_VIDEO_VOD = 'https://player.ooyala.com/sas/player_api/v2/authorization/' \
                'embed_code/%s/%s?device=html5&domain=www3.nhk.or.jp'
# pcode, Videoid

URL_GET_JS_PCODE = 'https://www3.nhk.or.jp/%s/common/player/tv/vod/'
# Channel_Name...

URL_WEATHER_NHK_NEWS = 'https://www3.nhk.or.jp/news/weather/weather_movie.json'

URL_NEWS_NHK_NEWS = 'http://www3.nhk.or.jp/news/json16/newmovie_%s.json'
# Page

URL_STREAM_NEWS = 'https://www3.nhk.or.jp/news/html/%s/movie/%s.json'
# Date, IdVideo

URL_NHK_LIFESTYLE = 'http://www.nhk.or.jp/lifestyle/'

URL_API_KEY_LIFE_STYLE = 'http://movie-s.nhk.or.jp/player.php?v=%s&wmode=transparen&r=true'
# VideoId

URL_STREAM_NHK_LIFE_STYLE = 'http://movie-s.nhk.or.jp/ws/ws_program/api/%s/apiv/5/mode/json?v=%s'
# Api_Key, VideoId

LOCATION = ['world']

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

CORRECT_MOUNTH = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}

def get_pcode(params):
    # Get js file
    file_path = utils.download_catalog(
        URL_GET_JS_PCODE % params.channel_name,
        '%s_js.html' % params.channel_name,
    )
    file_js = open(file_path).read()
    js_file = re.compile('<script src="\/(.+?)"').findall(file_js)

    # Get last JS script
    url_get_pcode = URL_ROOT + js_file[len(js_file)-1]

    # Get apikey
    file_path_js = utils.download_catalog(
        url_get_pcode,
        '%s_pcode.js' % params.channel_name,
    )
    pcode_js = open(file_path_js).read()
    pcode = re.compile('pcode: "(.+?)"').findall(pcode_js)
    return pcode[0]

def get_api_key(params):
    # Get apikey
    file_path_js = utils.download_catalog(
        URL_COMMONJS_NHK % params.channel_name,
        '%s_info.js' % params.channel_name,
    )
    info_js = open(file_path_js).read()

    apikey = re.compile('nw_api_key\|\|"(.+?)"').findall(info_js)
    return apikey[0]

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def root(params):
    modes = []

    if params.channel_name == 'nhknews':

        # Add News
        modes.append({
            'label' : 'ニュース',
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='list_videos_news',
                page='1',
                category='NHK ニュース',
                window_title='NHK ニュース'
            ),
        })

        # Add Weather
        modes.append({
            'label' : '気象',
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='list_videos_weather',
                category='NHK ニュース - 気象',
                window_title='NHK ニュース - 気象'
            ),
        })

    elif params.channel_name == 'nhkworld':

        # Add Replay
        modes.append({
            'label' : 'Replay',
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='list_shows_1',
                category='%s Replay' % params.channel_name.upper(),
                window_title='%s Replay' % params.channel_name.upper()
            ),
        })

        # Add Live
        modes.append({
            'label' : 'Live TV',
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='live_cat',
                category='%s Live TV' % params.channel_name.upper(),
                window_title='%s Live TV' % params.channel_name.upper()
            ),
        })

    elif params.channel_name == 'nhklifestyle':

        # Build Menu
        list_categories_html = utils.get_webcontent(URL_NHK_LIFESTYLE)
        list_categories_soup = bs(list_categories_html, 'html.parser')
        list_categories = list_categories_soup.find_all('a', class_="header__menu__head")

        for category in list_categories:
            if '#' not in category.get('href'):
                category_title = category.get_text().encode('utf-8')
                category_url = URL_NHK_LIFESTYLE + category.get('href')

                modes.append({
                    'label': category_title,
                    'url': common.PLUGIN.get_url(
                        action='channel_entry',
                        next='list_videos_lifestyle',
                            title=category_title,
                            category_url=category_url,
                            window_title=category_title
                        )
                    })

    return common.PLUGIN.create_listing(
        modes,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
    )

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    shows = []

    if params.next == 'list_shows_1':

        all_video = common.ADDON.get_localized_string(30101)

        shows.append({
            'label': all_video,
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='list_videos_cat',
                category_id=0,
                all_video=all_video,
                window_title=all_video
            ),
        })

        file_path = utils.download_catalog(
            URL_CATEGORIES_NHK % (params.channel_name, get_api_key(params)),
            '%s_categories.json' % (params.channel_name)
        )
        file_categories = open(file_path).read()
        json_parser = json.loads(file_categories)

        for category in json_parser["vod_categories"]:

            name_category = category["name"].encode('utf-8')
            category_id = category["category_id"]

            shows.append({
                'label': name_category,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='list_videos_cat',
                    category_id=category_id,
                    name_category=name_category,
                    window_title=name_category
                ),
            })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        )
    )

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    videos = []
    if 'previous_listing' in params:
        videos = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_videos_cat':
        category_id = params.category_id

        file_path = utils.download_catalog(
            URL_ALL_VOD_NHK % (params.channel_name, get_api_key(params)),
            '%s_all_vod.json' % (params.channel_name)
        )
        file_all_vod = open(file_path).read()
        json_parser = json.loads(file_all_vod)

        for episode in json_parser["data"]["episodes"]:

            episode_to_add = False

            if str(params.category_id) == '0':
                episode_to_add = True
            else:
                for category in episode["category"]:
                    if str(category) == str(params.category_id):
                        episode_to_add = True

            if episode_to_add is True:
                title = episode["title_clean"].encode('utf-8') + ' - ' + \
                        episode["sub_title_clean"].encode('utf-8')
                img = URL_ROOT + episode["image"].encode('utf-8')
                video_id = episode["vod_id"].encode('utf-8')
                plot = episode["description_clean"].encode('utf-8')
                duration = 0
                duration = episode["movie_duration"]

                value_date = time.strftime('%d %m %Y',
                             time.localtime(int(str(episode["onair"])[:-3])))
                date = str(value_date).split(' ')
                day = date[0]
                mounth = date[1]
                year = date[2]

                date = '.'.join((day, mounth, year))
                aired = '-'.join((year, mounth, day))

                info = {
                    'video': {
                        'title': title,
                        'plot': plot,
                        # 'episode': episode_number,
                        # 'season': season_number,
                        # 'rating': note,
                        'aired': aired,
                        'date': date,
                        'duration': duration,
                        'year': year,
                        'mediatype': 'tvshow'
                    }
                }

                context_menu = []
                download_video = (
                    _('Download'),
                    'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                        action='download_video',
                        video_id=video_id) + ')'
                )
                context_menu.append(download_video)

                videos.append({
                    'label': title,
                    'thumb': img,
                    'fanart': img,
                    'url': common.PLUGIN.get_url(
                        action='channel_entry',
                        next='play_r',
                        video_id=video_id
                    ),
                    'is_playable': True,
                    'info': info,
                    'context_menu': context_menu
                })

    elif params.next == 'list_videos_weather':

        file_path = utils.download_catalog(
            URL_WEATHER_NHK_NEWS,
            '%s_weather.json' % (params.channel_name)
        )
        file_weather = open(file_path).read()
        json_parser = json.loads(file_weather)

        title = json_parser["va"]["adobe"]["vodContentsID"]["VInfo1"]
        img = URL_ROOT + json_parser["mediaResource"]["posterframe"]
        duration = 0
        video_url = json_parser["mediaResource"]["url"]

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

        context_menu = []
        download_video = (
            _('Download'),
            'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                action='download_video',
                video_url=video_url) + ')'
        )
        context_menu.append(download_video)

        videos.append({
            'label': title,
            'thumb': img,
            'fanart': img,
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='play_weather_r',
                video_url=video_url
            ),
            'is_playable': True,
            'info': info,
            'context_menu': context_menu
        })

    elif params.next == 'list_videos_news':

        # Build URL :
        url = ''
        if int(params.page) < 10:
            url = URL_NEWS_NHK_NEWS % ('00' + params.page)
        elif int(params.page) >= 10 and int(params.page) < 100:
            url = URL_NEWS_NHK_NEWS % ('0' + params.page)
        else:
            url = URL_NEWS_NHK_NEWS % params.page
        file_path = utils.download_catalog(
            url,
            '%s_news_%s.json' % (params.channel_name, params.page)
        )
        file_news = open(file_path).read()
        json_parser = json.loads(file_news)

        for video in json_parser["channel"]["item"]:
            title = video["title"]
            img = URL_ROOT + 'news/' + video["imgPath"]
            duration = int(video["videoDuration"])
            video_id = video["videoPath"].replace('.mp4','')
            pub_date_list = video["pubDate"].split(' ')

            if len(pub_date_list[1]) == 1:
                day = '0' + pub_date_list[0]
            else:
                day = pub_date_list[1]
            try:
                mounth = CORRECT_MOUNTH[pub_date_list[2]]
            except:
                mounth = '00'
            year = pub_date_list[3]

            date = '.'.join((day, mounth, year))
            aired = '-'.join((year, mounth, day))

            video_date = ''.join((year, mounth, day))

            info = {
                'video': {
                    'title': title,
                    # 'plot': plot,
                    # 'episode': episode_number,
                    # 'season': season_number,
                    # 'rating': note,
                    'aired': aired,
                    'date': date,
                    'duration': duration,
                    'year': year,
                    'mediatype': 'tvshow'
                }
            }

            context_menu = []
            download_video = (
                _('Download'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='download_video',
                    video_id=video_id,
                    video_date=video_date) + ')'
            )
            context_menu.append(download_video)

            videos.append({
                'label': title,
                'thumb': img,
                'fanart': img,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='play_news_r',
                    video_id=video_id,
                    video_date=video_date
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

        # More videos...
        videos.append({
            'label': '# ' + common.ADDON.get_localized_string(30100),
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='list_videos_news',
                page=str(int(params.page) + 1),
                update_listing=True,
                previous_listing=str(videos)
            ),
        })

    elif params.next == 'list_videos_lifestyle':

        replay_episodes_html = utils.get_webcontent(params.category_url)
        replay_episodes_soup = bs(replay_episodes_html, 'html.parser')
        episodes_html = replay_episodes_soup.find('article')
        episodes_html = episodes_html.find_all('script')[0].get_text().encode('utf-8')
        replay_episodes_json = episodes_html.replace(']', '')
        replay_episodes_json = replay_episodes_json.replace('var NHKLIFE_LISTDATA = [', '')
        replay_episodes_json = replay_episodes_json.strip()
        replay_episodes_json = replay_episodes_json.replace('{', '{"')
        replay_episodes_json = replay_episodes_json.replace(': ', '": ')
        replay_episodes_json = replay_episodes_json.replace(',', ',"')
        replay_episodes_json = replay_episodes_json.replace(',"{', ',{')
        json_parser = json.loads('[' + replay_episodes_json + ']')

        for video in json_parser:
            if 'video' in video["href"]:
                title = video["title"]
                plot = video["desc"]
                img = URL_ROOT_2 + video["image_src"]
                duration = 60 * int(video["videoInfo"]["duration"].split(':')[0]) + \
                           int(video["videoInfo"]["duration"].split(':')[1])
                video_url = URL_NHK_LIFESTYLE + \
                            video["href"].replace('../','')

                # published_date: "2017年10月10日"
                # year = video["published_date"].encode('utf-8').split('年')[0]
                # mounth = video["published_date"].encode('utf-8').split('年')[1].split['月'][0]
                # day = video["published_date"].encode('utf-8').split('月')[1].split['日'][0]

                # date = '.'.join((day, mounth, year))
                # aired = '-'.join((year, mounth, day))

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

                context_menu = []
                download_video = (
                    _('Download'),
                    'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                        action='download_video',
                        video_url=video_url) + ')'
                )
                context_menu.append(download_video)

                videos.append({
                    'label': title,
                    'thumb': img,
                    'fanart': img,
                    'url': common.PLUGIN.get_url(
                        action='channel_entry',
                        next='play_lifestyle_r',
                        video_url=video_url
                    ),
                    'is_playable': True,
                    'info': info,
                    'context_menu': context_menu
                })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_DATE,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
            common.sp.xbmcplugin.SORT_METHOD_GENRE,
            common.sp.xbmcplugin.SORT_METHOD_PLAYCOUNT,
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        content='tvshows',
        update_listing='update_listing' in params,
    )

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_live(params):

    lives = []

    title = ''
    subtitle = ' - '
    plot = ''
    duration = 0
    img = ''
    url_live = ''

    title = '%s Live' % (params.channel_name.upper())

    # Get URL Live
    file_path = utils.download_catalog(
        URL_LIVE_NHK % params.channel_name,
        '%s_live.xml' % params.channel_name,
    )
    live_xml = open(file_path).read()
    xmlElements = ET.XML(live_xml)
    url_live = xmlElements.find("tv_url").findtext("wstrm").encode('utf-8')

    # GET Info Live (JSON)
    url_json = URL_LIVE_INFO_NHK % (params.channel_name,
               LOCATION[0], get_api_key(params))
    file_path_json = utils.download_catalog(
        url_json,
        '%s_live.json' % params.channel_name,
    )
    live_json = open(file_path_json).read()
    json_parser = json.loads(live_json)

    # Get First Element
    for info_live in json_parser['channel']['item']:
        if info_live["subtitle"] != '':
            subtitle = subtitle + info_live["subtitle"].encode('utf-8')
        title = info_live["title"].encode('utf-8') + subtitle

        start_date = time.strftime('%H:%M',
                     time.localtime(int(str(info_live["pubDate"])[:-3])))
        end_date = time.strftime('%H:%M',
                   time.localtime(int(str(info_live["endDate"])[:-3])))
        plot = start_date + ' - ' + end_date + '\n ' + \
               info_live["description"].encode('utf-8')
        img = URL_ROOT + info_live["thumbnail"].encode('utf-8')
        break

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
        'url': common.PLUGIN.get_url(
            action='channel_entry',
            next='play_l',
            url=url_live,
        ),
        'is_playable': True,
        'info': info
    })

    return common.PLUGIN.create_listing(
        lives,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        )
    )

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_video_url(params):

    if params.next == 'play_r' or params.next == 'download_video':
        url = ''
        file_path = utils.download_catalog(
            URL_VIDEO_VOD % (get_pcode(params), params.video_id),
            '%s_%s_video_vod.json' % (params.channel_name, params.video_id)
        )
        video_vod = open(file_path).read()
        json_parser = json.loads(video_vod)

        # Get Value url encodebase64
        for stream in json_parser["authorization_data"][params.video_id]["streams"]:
            url_base64 = stream["url"]["data"]
        url = base64.standard_b64decode(url_base64)
        return url
    elif params.next == 'play_l':
        return params.url
    elif params.next == 'play_weather_r':
        return params.video_url
    elif params.next == 'play_news_r':
        url = ''
        file_path = utils.download_catalog(
            URL_STREAM_NEWS % (params.video_date, params.video_id),
            '%s_%s.json' % (params.channel_name, params.video_id)
        )
        video_vod = open(file_path).read()
        json_parser = json.loads(video_vod)
        return json_parser["mediaResource"]["url"]
    elif params.next == 'play_lifestyle_r':
        video_id_html = utils.get_webcontent(params.video_url)
        video_id = re.compile('player.php\?v=(.*?)&').findall(video_id_html)[0]
        api_key_html = utils.get_webcontent(URL_API_KEY_LIFE_STYLE % video_id)
        api_key = re.compile('data-de-api-key="(.*?)"').findall(api_key_html)[0]
        url_stream = URL_STREAM_NHK_LIFE_STYLE % (api_key, video_id)
        url_stream_json = utils.get_webcontent(url_stream)
        json_parser_stream = json.loads(url_stream_json)
        return json_parser_stream["response"]["WsProgramResponse"]["program"]["asset"]["ipadM3u8Url"]
