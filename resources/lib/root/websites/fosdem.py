# -*- coding: utf-8 -*-
'''
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
'''

import xml.etree.ElementTree as ET
from resources.lib import utils
from resources.lib import common

# TO DO
# YEARS BEFORE 2012 (VIDEO in different format and accessible differently)

URL_SCHEDULE_XML = 'https://fosdem.org/%s/schedule/xml'
# Year

BEGINING_YEAR_XML = 2012
LAST_YEAR_XML = 2018


def website_entry(params):
    """Entry function of the module"""
    if 'root' in params.next:
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
    """Add modes in the listing"""
    modes = []

    for i in range(BEGINING_YEAR_XML, LAST_YEAR_XML + 1):
        year_label = str(i)
        category_title = year_label
        category_url = URL_SCHEDULE_XML % year_label

        modes.append({
            'label': category_title,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='website_entry',
                next='list_videos_1',
                title=category_title,
                category_url=category_url,
                window_title=category_title
            )
        })

    return common.PLUGIN.create_listing(
        modes,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []

    if params.next == 'list_videos_1':

        videos_datas_xml = utils.get_webcontent(
            params.category_url)
        xml_elements = ET.XML(videos_datas_xml)

        for video in xml_elements.findall(".//event"):

            video_links = video.findall(".//link")
            video_url = ''
            for video_link in video_links:
                if 'Video' in video_link.text.encode('utf-8'):
                    video_url = video_link.get('href')

            if video_url != '':
                video_title = video.find("title").text.encode('utf-8')
                video_duration = 0
                video_plot = ''
                if video.find("abstract").text:
                    video_plot = video.find("abstract").text.encode('utf-8')

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
                        video_url=video_url) + ')'
                )
                context_menu = []
                context_menu.append(download_video)

                videos.append({
                    'label': video_title,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='website_entry',
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
        update_listing='update_listing' in params,
        category=common.get_window_title(params)
    )


def get_video_url(params):
    """Get video URL and start video player"""
    return params.video_url
