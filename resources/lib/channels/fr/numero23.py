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

from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common
import re

url_root = 'http://www.numero23.fr/programmes/'


def channel_entry(params):
    if 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)
    else:
        return None


@common.plugin.cached(common.cache_time)
def list_shows(params):
    shows = []
    if params.next == 'list_shows_1':
        file_path = utils.download_catalog(
            url_root,
            params.channel_name + '.html')
        root_html = open(file_path).read()
        root_soup = bs(root_html, 'html.parser')

        categories_soup = root_soup.find(
            'div',
            class_='content'
        )

        for category in categories_soup.find_all('h2'):
            category_name = category.get_text().encode('utf-8')
            category_hash = common.sp.md5(category_name).hexdigest()

            shows.append({
                'label': category_name,
                'url': common.plugin.get_url(
                    action='channel_entry',
                    category_hash=category_hash,
                    next='list_shows_pgms',
                    window_title=category_name,
                    category_name=category_name,
                )
            })

    elif params.next == 'list_shows_pgms':
        file_path = utils.download_catalog(
            url_root,
            params.channel_name + '.html')
        root_html = open(file_path).read()
        root_soup = bs(root_html, 'html.parser')

        categories_soup = root_soup.find(
            'div',
            class_='content'
        )

        for category in categories_soup.find_all('h2'):
            category_name = category.get_text().encode('utf-8')
            category_hash = common.sp.md5(category_name).hexdigest()

            print category_hash
            print params.category_hash

            if params.category_hash == category_hash:
                programs = category.find_next('div')
                for program in programs.find_all('div', class_='program'):
                    program_name_url = program.find('h3').find('a')
                    program_name = program_name_url.get_text().encode('utf-8')
                    program_url = program_name_url['href'].encode('utf-8')
                    program_img = program.find('img')['src'].encode('utf-8')

                    shows.append({
                        'label': program_name,
                        'thumb': program_img,
                        'url': common.plugin.get_url(
                            action='channel_entry',
                            program_url=program_url,
                            next='list_videos',
                            window_title=program_name,
                            program_name=program_name
                        )
                    })

    return common.plugin.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
    )


@common.plugin.cached(common.cache_time)
def list_videos(params):
    videos = []

    file_path = utils.download_catalog(
        params.program_url,
        '%s_%s.html' % (params.channel_name, params.program_name)
    )
    program_html = open(file_path).read()
    program_soup = bs(program_html, 'html.parser')

    videos_soup = program_soup.find_all('div', class_='box program')

    if len(videos_soup) == 0:
        videos_soup = program_soup.find_all(
            'div', class_='program sticky video')

    for video in videos_soup:
        video_title = video.find(
            'p').get_text().encode('utf-8').replace(
                '\n', ' ').replace('\r', ' ').rstrip('\r\n')
        video_img = video.find('img')['src'].encode('utf-8')
        video_url = video.find('a')['href'].encode('utf-8')

        info = {
            'video': {
                'title': video_title,
                'mediatype': 'tvshow'
            }
        }

        videos.append({
            'label': video_title,
            'thumb': video_img,
            'url': common.plugin.get_url(
                action='channel_entry',
                next='play',
                video_url=video_url
            ),
            'is_playable': True,
            'info': info
        })

    return common.plugin.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE
        ),
        content='tvshows')


@common.plugin.cached(common.cache_time)
def get_video_url(params):
    video_html = utils.get_webcontent(
        params.video_url
    )
    video_soup = bs(video_html, 'html.parser')
    video_id = video_soup.find(
        'div', class_='video')['data-video-id'].encode('utf-8')

    url_daily = 'http://www.dailymotion.com/embed/video/' + video_id

    html_daily = utils.get_webcontent(
        url_daily,)

    html_daily = html_daily.replace('\\', '')

    urls_mp4 = re.compile(
        r'{"type":"video/mp4","url":"(.*?)"}],"(.*?)"').findall(html_daily)

    url_sd = ""
    url_hd = ""
    url_hdplus = ""
    url_default = ""

    for url, quality in urls_mp4:
        if quality == '480':
            url_sd = url
        elif quality == '720':
            url_hd = url
        elif quality == '1080':
            url_hdplus = url
        url_default = url

    desired_quality = common.plugin.get_setting(
        params.channel_id + '.quality')

    if desired_quality == 'HD+' and url_hdplus:
        return url_hdplus
    elif desired_quality == 'HD' and url_hd:
        return url_hd
    elif desired_quality == 'SD' and url_sd:
        return url_sd
    else:
        return url_default
