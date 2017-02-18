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

from resources.lib import utils
from resources.lib import common
from bs4 import BeautifulSoup as bs

url_replay = 'http://www.nrj-play.fr/%s/replay'
# channel_name (nrj12, ...)

url_root = 'http://www.nrj-play.fr'


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

    if 'list_shows_1' in params.next:
        # Build categories list (Tous les programmes, Séries, ...)
        file_path = utils.download_catalog(
            url_replay % params.channel_name,
            '%s_replay.html' % params.channel_name,
        )
        replay_html = open(file_path).read()
        replay_soup = bs(replay_html, 'html.parser')

        categories_soup = replay_soup.find_all(
            'li',
            class_='subNav-menu-item')

        for category in categories_soup:
            url_category = category.find('a')['href'].encode('utf-8')
            title_category = category.find('a').get_text().encode('utf-8')

            shows.append({
                'label': title_category,
                'url': common.plugin.get_url(
                    action='channel_entry',
                    url_category=url_category,
                    next='list_shows_cat',
                    title=title_category
                )
            })

        return common.plugin.create_listing(
            shows,
            sort_methods=(
                common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
                common.sp.xbmcplugin.SORT_METHOD_LABEL
            )
        )

    elif 'list_shows_cat' in params.next:
        # Build category's programs list
        file_path = utils.download_catalog(
            url_root + params.url_category,
            '%s_%s.html' % (params.channel_name, params.title),
        )
        category_html = open(file_path).read()
        category_soup = bs(category_html, 'html.parser')

        programs_soup = category_soup.find_all(
            'div',
            class_='linkProgram')

        for program in programs_soup:
            title = program.find(
                'h2',
                class_='linkProgram-title').get_text().encode('utf-8')

            title = ' '.join(title.split())

            url = program.find('a')['href'].encode('utf-8')
            img = program.find('img')['src'].encode('utf-8')

            shows.append({
                'label': title,
                'thumb': img,
                'url': common.plugin.get_url(
                    action='channel_entry',
                    next='list_videos',
                    url_program=url,
                    title=title
                ),
            })

        return common.plugin.create_listing(
            shows,
            sort_methods=(
                common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
                common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE
            ),
        )

@common.plugin.cached(common.cache_time)
def list_videos(params):
    videos = []

    # Build program's videos list
    file_path = utils.download_catalog(
        url_root + params.url_program,
        '%s_%s.html' % (params.channel_name, params.title),
    )
    program_html = open(file_path).read()
    program_soup = bs(program_html, 'html.parser')

    program_soup_2 = program_soup.find(
        'section',
        class_='section-replay')

    if program_soup_2:
        videos_soup = program_soup_2.find_all('div', class_='item')
        for video in videos_soup:
            title_soup = video.find(
                'h3',
                class_='thumbnail-title')
            title = title_soup.get_text().encode('utf-8')
            title = ' '.join(title.split())

            url = title_soup.find('a')['href'].encode('utf-8')
            img = video.find('img')['src'].encode('utf-8')
            date = video.find('time').get_text().encode('utf-8').split(' ')[1]
            date_splited = date.split('/')
            day = date_splited[0]
            mounth = date_splited[1]
            year = date_splited[2]

            date = '.'.join((day, mounth, year))
            aired = '-'.join((year, mounth, day))
            # date : string (%d.%m.%Y / 01.01.2009)
            # aired : string (2008-12-07)
            info = {
                'video': {
                    'title': title,
                    'aired': aired,
                    'date': date,
                    'year': year
                }
            }

            videos.append({
                'label': title,
                'thumb': img,
                'url': common.plugin.get_url(
                    action='channel_entry',
                    next='play',
                    url_video=url
                ),
                'is_playable': True,
                'info': info
            })

    else:
        title_soup = program_soup.find(
            'meta',
            attrs={'itemprop': 'thumbnailUrl'})
        title = title_soup['alt'].encode('utf-8')
        img = title_soup['content'].encode('utf-8')
        # TODO : desc, date, duration
        info = {
            'video': {
                'title': title
                # 'aired': aired,
                # 'date': date,
                # 'year': year
            }
        }
        videos.append({
            'label': title,
            'thumb': img,
            'url': common.plugin.get_url(
                action='channel_entry',
                next='play',
                url_video=params.url_program
            ),
            'is_playable': True,
            'info': info
        })

    return common.plugin.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_DATE,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE
        ),
        content='tvshows')


@common.plugin.cached(common.cache_time)
def get_video_url(params):
    video_html = utils.get_webcontent(
        url_root + params.url_video)
    video_soup = bs(video_html, 'html.parser')
    print video_soup
    return video_soup.find(
        'meta',
        attrs={'itemprop': 'contentUrl'})['content'].encode('utf-8')
