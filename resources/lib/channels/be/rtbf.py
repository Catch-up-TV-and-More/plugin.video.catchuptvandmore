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
import ast
import re
import json

url_json_categories = 'https://www.rtbf.be/news/api/menu?site=media'

url_more_subcategories = 'https://www.rtbf.be/news/api/block?data%%5B0%%5D%%5B' \
                         'uuid%%5D=%s&data%%5B0%%5D%%5Btype%%5D=widget&data%%5B0%%' \
                         '5D%%5Bsettings%%5D%%5Bid%%5D=%s&data%%5B0%%5D%%5Bsettings' \
                         '%%5D%%5Bparams%%5D%%5Border%%5D=0'
# widget-10097-58bdd52f55880, 10097
channel_filter = {
    'laune': 'La Une',
    'ladeux': 'La Deux',
    'latrois': 'La Trois'
}


def channel_entry(params):
    if 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)
    else:
        return None


#@common.plugin.cached(common.cache_time)
def list_shows(params):
    shows = []
    # if 'previous_listing' in params:
    #     shows = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_shows_1':
        file_path = utils.download_catalog(
            url_json_categories,
            '%s_categories.json' % params.channel_name)
        categories_json = open(file_path).read()
        categories = json.loads(categories_json)

        for category in categories['item']:
            if category['@attributes']['id'] == 'emission':
                category_title = category[
                    '@attributes']['name'].encode('utf-8')
                category_url = category[
                    '@attributes']['url'].encode('utf-8')
                shows.append({
                    'label': category_title,
                    'url': common.plugin.get_url(
                        category_title=category_title,
                        action='channel_entry',
                        category_url=category_url,
                        next='list_shows_cat',
                        window_title=category_title
                    )
                })

            elif category['@attributes']['id'] == 'category':
                for sub_category in category['item']:
                    if 'category' in sub_category['@attributes']['id']:
                        category_title = sub_category[
                            '@attributes']['name'].encode('utf-8')
                        category_url = sub_category[
                            '@attributes']['url'].encode('utf-8')
                        shows.append({
                            'label': category_title,
                            'url': common.plugin.get_url(
                                category_title=category_title,
                                action='channel_entry',
                                category_url=category_url,
                                next='list_shows_cat',
                                window_title=category_title
                            )
                        })

    elif params.next == 'list_shows_cat':
        file_path = utils.download_catalog(
            params.category_url,
            '%s_%s.html' % (
                params.channel_name,
                params.category_title))
        category_html = open(file_path).read()
        category_soup = bs(category_html, 'html.parser')


        widgets_soup = category_soup.find_all('b', class_='js-block')
        for widget_soup in widgets_soup:
            uuid = widget_soup['data-uuid'].encode('utf-8')
            uuid_main = uuid.split('-')[1]
            widget_json = utils.get_webcontent(
                url_more_subcategories % (uuid, uuid_main))
            widget = json.loads(widget_json)
            widget_html = widget['blocks'][uuid].encode('utf-8')
            category_html += widget_html

        category_soup = bs(category_html, 'html.parser')

        for category in category_soup.find_all('div', class_='www-row'):
            title = category.find('h2').get_text().encode('utf-8')
            title = ' '.join(title.split())
            print title


        # for category_soup in categories_soup.find_all('li'):
        #     category_title = category_soup.find(
        #         'a').get_text().encode('utf-8').replace(
        #             '\n', '').replace(' ', '')
        #     category_url = category_soup.find(
        #         'a')['href'].encode('utf-8').replace('//', 'http://')

        #     shows.append({
        #         'label': category_title,
        #         'url': common.plugin.get_url(
        #             category_title=category_title,
        #             action='channel_entry',
        #             category_url=category_url,
        #             next='list_shows_cat',
        #             window_title=category_title,
        #             index_page='1'
        #         )
        #     })

    # elif params.next == 'list_shows_cat':
    #     file_path = utils.download_catalog(
    #         params.category_url,
    #         '%s_%s_%s.html' % (
    #             params.channel_name,
    #             params.category_title,
    #             params.index_page))
    #     category_html = open(file_path).read()
    #     category_soup = bs(category_html, 'html.parser')

    #     programs_soup = category_soup.find_all(
    #         'article',
    #         attrs={'card': 'tv-show'})

    #     for program_soup in programs_soup:
    #         program_title = program_soup.find('h3').get_text().encode('utf-8')
    #         program_url = program_soup.find(
    #             'a')['href'].encode('utf-8').replace('//', 'http://')
    #         program_url = program_url + '/videos'
    #         program_img = program_soup.find(
    #             'img')['src'].encode('utf-8').replace('//', 'http://')
    #         program_img = utils.get_redirected_url(program_img)

    #         shows.append({
    #             'label': program_title,
    #             'thumb': program_img,
    #             'url': common.plugin.get_url(
    #                 program_title=program_title,
    #                 action='channel_entry',
    #                 program_url=program_url,
    #                 next='list_videos',
    #                 window_title=program_title
    #             )
    #         })

    #     if category_soup.find('nav', attrs={'pagination': 'infinite'}):
    #         url = category_soup.find(
    #             'nav', attrs={'pagination': 'infinite'}).find(
    #             'a')['href'].encode('utf-8').replace('//', 'http://')
    #         # More programs...
    #         shows.append({
    #             'label': common.addon.get_localized_string(30108),
    #             'url': common.plugin.get_url(
    #                 category_title=params.category_title,
    #                 action='channel_entry',
    #                 category_url=url,
    #                 next=params.next,
    #                 window_title=params.category_title,
    #                 index_page=str(int(params.index_page) + 1),
    #                 update_listing=True,
    #                 previous_listing=str(shows)
    #             )

    #         })

    return common.plugin.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        update_listing='update_listing' in params
    )


#@common.plugin.cached(common.cache_time)
def list_videos(params):
    videos = []
    return videos
    # if 'previous_listing' in params:
    #     videos = ast.literal_eval(params['previous_listing'])

    # if 'index_page' in params:
    #     index_page = params.index_page
    # else:
    #     index_page = '1'

    # if 'category_url' in params:
    #     url = params.category_url
    # else:
    #     url = params.program_url

    # if 'category_title' in params:
    #     title = params.category_title
    # else:
    #     title = params.program_title

    # videos_len_bool = False
    # if 'videos_len' in params:
    #     videos_len = int(params.videos_len)
    #     if videos_len != -1:
    #         videos_len_bool = True

    # file_path = utils.download_catalog(
    #     url,
    #     '%s_%s_%s.html' % (
    #         params.channel_name,
    #         title,
    #         index_page))
    # videos_html = open(file_path).read()
    # videos_soup = bs(videos_html, 'html.parser')

    # videos_soup_2 = videos_soup.find_all(
    #     'article',
    #     attrs={'card': 'video'})

    # if videos_len_bool is True:
    #     videos_soup_2.insert(0, videos_soup.find_all(
    #         'article',
    #         attrs={'card': 'big-video'})[0])

    # count = 0

    # for video_soup in videos_soup_2:
    #     if videos_len_bool is True and count > videos_len:
    #         break
    #     count += 1
    #     video_content = video_soup.find('div', class_='content')
    #     video_title = video_content.find(
    #         'a').get_text().encode('utf-8')
    #     video_subtitle = video_content.find(
    #         'h3').get_text().encode('utf-8')
    #     video_url = video_soup.find(
    #         'a')['href'].encode('utf-8').replace('//', 'http://')

    #     video_img = video_soup.find(
    #         'img')['src'].encode('utf-8').replace('//', 'http://')
    #     video_img = utils.get_redirected_url(video_img)

    #     try:
    #         video_aired = video_soup.find('time')['datetime'].encode('utf-8')
    #         video_aired = video_aired.split('T')[0]
    #         video_aired_splited = video_aired.split('-')

    #         day = video_aired_splited[2]
    #         mounth = video_aired_splited[1]
    #         year = video_aired_splited[0]
    #         video_date = '.'.join((day, mounth, year))
    #         # date : string (%d.%m.%Y / 01.01.2009)
    #         # aired : string (2008-12-07)
    #     except:
    #         year = 0
    #         video_aired = ''
    #         video_date = ''

    #     if video_subtitle:
    #         video_title = video_title + ' - [I]' + video_subtitle + '[/I]'

    #     info = {
    #         'video': {
    #             'title': video_title,
    #             'aired': video_aired,
    #             'date': video_date,
    #             'year': int(year),
    #             'mediatype': 'tvshow'
    #         }
    #     }

    #     videos.append({
    #         'label': video_title,
    #         'thumb': video_img,
    #         'url': common.plugin.get_url(
    #             action='channel_entry',
    #             next='play',
    #             video_url=video_url
    #         ),
    #         'is_playable': True,
    #         'info': info
    #     })

    # if videos_len_bool is False:
    #     prev_next_soup = videos_soup.find(
    #         'div',
    #         attrs={'pagination': 'prev-next'})
    #     if prev_next_soup.find('a', class_='next'):
    #         url = prev_next_soup.find(
    #             'a', class_='next')['href'].encode('utf-8').replace('//', '')
    #         url = 'http://' + url
    #         # More videos...
    #         videos.append({
    #             'label': common.addon.get_localized_string(30100),
    #             'url': common.plugin.get_url(
    #                 category_title=title,
    #                 action='channel_entry',
    #                 category_url=url,
    #                 next=params.next,
    #                 window_title=title,
    #                 index_page=str(int(index_page) + 1),
    #                 update_listing=True,
    #                 previous_listing=str(videos)
    #             )

    #         })

    # return common.plugin.create_listing(
    #     videos,
    #     sort_methods=(
    #         common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
    #         common.sp.xbmcplugin.SORT_METHOD_DATE,
    #         common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE
    #     ),
    #     content='tvshows',
    #     update_listing='update_listing' in params)


#@common.plugin.cached(common.cache_time)
def get_video_url(params):
    return None
