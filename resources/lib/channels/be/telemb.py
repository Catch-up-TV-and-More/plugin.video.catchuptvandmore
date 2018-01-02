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
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common

# TO DO
# Add Live when it is working
# RSS get more video ?

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

URL_ROOT = 'https://www.telemb.be'

URL_VIDEOS = 'https://www.telemb.be/rss.php?id_menu=%s'
# CategoryId

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
            window_title='%s Replay' % params.channel_name.upper()
        )
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

        replay_categories_html = utils.get_webcontent(URL_ROOT)
        replay_categories_soup = bs(replay_categories_html, 'html.parser')
        categories = replay_categories_soup.find(
            'ul', class_='nav nav-pills pull-right').find_all(
                'li', class_='menu-item menu-item-type-post_type menu-item-object-page')

        for category in categories:
            if 'meteo' in category.find('a').get('href') or \
               'actualite' in category.find('a').get('href') or \
               'sports' in category.find('a').get('href') or \
               'emissions' in category.find('a').get('href'):

                category_name = category.find('a').get_text()
                category_id = category.find('a').get(
                    'href').split('.html')[0].split('c_')[1]
                shows.append({
                    'label': category_name,
                    'url': common.PLUGIN.get_url(
                        action='channel_entry',
                        category_id=category_id,
                        category_name=category_name,
                        next='list_videos_1',
                        page='1',
                        window_title=category_name
                    )
                })

                sub_categories = category.find_all(
                    'li', class_='menu-item menu-item-type-post_type menu-item-object-post')
                for sub_category in sub_categories:

                    category_name = sub_category.find('a').get_text()
                    category_id = sub_category.find("a").get(
                        "href").split('.html')[0].split('c_')[1]
                    shows.append({
                        'label': category_name,
                        'url': common.PLUGIN.get_url(
                            action='channel_entry',
                            category_id=category_id,
                            category_name=category_name,
                            next='list_videos_1',
                            page='1',
                            window_title=category_name
                        )
                    })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []

    videos_html = utils.get_webcontent(
        URL_VIDEOS % (params.category_id))
    videos_html = videos_html.strip()
    videos_html = videos_html.replace('&', '&amp;')
    xml_elements = ET.XML(videos_html)
    # TO DO Some xml not well formated
    for video in xml_elements.find("channel").findall("item"):

        title = video.find("title").text.encode('utf-8')
        duration = 0
        video_url = video.find("link").text.encode('utf-8')
        img = video.find("enclosure").get('url').encode('utf-8')
        plot = video.find("description").text.encode('utf-8')

        info = {
            'video': {
                'title': title,
                # 'aired': aired,
                # 'date': date,
                'plot': plot,
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
            common.sp.xbmcplugin.SORT_METHOD_PLAYCOUNT,
            common.sp.xbmcplugin.SORT_METHOD_DATE,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE
        ),
        content='tvshows',
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_live(params):
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_video_url(params):
    """Get video URL and start video player"""
    url_stream = ''
    if params.next == 'play_r' or params.next == 'download_video':
        video_html = utils.get_webcontent(
            params.video_url)
        urls_video = re.compile(
            r'file\: "(.*?)"').findall(video_html)
        for url_video in urls_video:
            if 'm3u8' in url_video:
                url_stream = url_video
    return url_stream
