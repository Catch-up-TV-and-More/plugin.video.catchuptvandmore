# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2019  SylvainCecchetto

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

# The unicode_literals import only has
# an effect on Python 2.
# It makes string literals as unicode like in Python 3
from __future__ import unicode_literals

from codequick import Route, Resolver, Listitem, utils, Script

from resources.lib.labels import LABELS
from resources.lib import web_utils
from resources.lib import resolver_proxy

import re
import urlquick

# TO DO
# Replay add emissions

URL_ROOT_FR = 'https://francais.rt.com'

URL_LIVE_FR = URL_ROOT_FR + '/en-direct'

URL_LIVE_EN = 'https://www.rt.com/on-air/'

URL_LIVE_AR = 'https://arabic.rt.com/live/'

URL_LIVE_ES = 'https://actualidad.rt.com/en_vivo'

# URL_VIDEOS = 'URL_ROOT_%s' % DESIRED_LANGUAGE + '/listing/program.%s/prepare/idi-listing/10/%s'

DESIRED_LANGUAGE = Script.setting['rt.language']

CATEGORIES_VIDEOS_FR = {
    URL_ROOT_FR + '/magazines': 'Magazines',
    URL_ROOT_FR + '/documentaires': 'Documentaires',
    URL_ROOT_FR + '/videos': 'Vidéos'
}


def replay_entry(plugin, item_id):
    """
    First executed function after replay_bridge
    """
    return list_categories(plugin, item_id)


@Route.register
def list_categories(plugin, item_id):
    """
    Build categories listing
    - Tous les programmes
    - Séries
    - Informations
    - ...
    """
    if DESIRED_LANGUAGE == 'FR':
        CATEGORIES_VIDEOS = eval('CATEGORIES_VIDEOS_%s' % DESIRED_LANGUAGE)
        for category_url, category_title in CATEGORIES_VIDEOS.iteritems():
            if 'magazines' in category_url:
                item = Listitem()
                item.label = category_title
                item.set_callback(
                    list_programs,
                    item_id=item_id,
                    next_url=category_url)
                yield item
            elif 'documentaires' in category_url:
                item = Listitem()
                item.label = category_title
                item.set_callback(
                    list_videos_documentaries,
                    item_id=item_id,
                    next_url=category_url,
                    page='0')
                yield item
            else:
                item = Listitem()
                item.label = category_title
                item.set_callback(
                    list_videos,
                    item_id=item_id,
                    page='0')
                yield item

        # Search videos
        # item = Listitem.search(
        #     list_videos_search,
        #     item_id=item_id,
        #     page='0')
        # yield item
    else:
        print 'TO_BE_IMPLEMENTED'


@Route.register
def list_programs(plugin, item_id, next_url):
    """
    Build programs listing
    - Les feux de l'amour
    - ...
    """
    resp = urlquick.get(next_url)
    root = resp.parse("ul", attrs={"class": "media-rows"})

    for program_datas in root.iterfind("li"):
        program_title = program_datas.find('.//img').get('alt')
        program_url = eval('URL_ROOT_%s' % DESIRED_LANGUAGE) + program_datas.find(
            './/a').get('href')
        program_image = program_datas.find('.//img').get('data-src')
        program_plot = program_datas.find('.//p').text

        item = Listitem()
        item.label = program_title
        item.art['thumb'] = program_image
        item.info['plot'] = program_plot
        item.set_callback(
            list_videos_programs,
            item_id=item_id,
            next_url=program_url,
            page='0')
        yield item


@Route.register
def list_videos_programs(plugin, item_id, next_url, page):

    resp = urlquick.get(next_url)
    program_id = re.compile(
        r'pageID \= \"(.*?)\"').findall(resp.text)[0]

    resp2 = urlquick.get(
        eval('URL_ROOT_%s' % DESIRED_LANGUAGE) + '/listing/program.%s/prepare/idi-listing/10/%s' % (program_id, page))

    root = resp2.parse("div", attrs={"data-role": "content"})

    for video_datas in root.iterfind(".//div[@data-role='item']"):
        video_title = video_datas.find(".//span[@class='st-idi-episode-card__title']").text.strip()
        video_image_datas = video_datas.find(".//span[@class='st-idi-episode-card__image']").get('style')
        video_image = re.compile(
            r'url\((.*?)\)').findall(video_image_datas)[0]
        video_url = video_datas.find('.//a').get('href')
        video_plot = video_datas.find(".//span[@class='st-idi-episode-card__summary']").text.strip()

        item = Listitem()
        item.label = video_title
        item.art['thumb'] = video_image
        item.info['plot'] = video_plot

        item.context.script(
            get_video_url,
            plugin.localize(LABELS['Download']),
            item_id=item_id,
            video_url=video_url,
            video_label=LABELS[item_id] + ' - ' + item.label,
            download_mode=True)

        item.set_callback(
            get_video_url,
            item_id=item_id,
            video_url=video_url)
        yield item

    yield Listitem.next_page(
        item_id=item_id,
        next_url=next_url,
        page=str(int(page) + 1))


@Route.register
def list_videos_documentaries(plugin, item_id, next_url, page):

    resp = urlquick.get(next_url)
    program_id = re.compile(
        r'\/program\.(.*?)\/prepare').findall(resp.text)[0]

    resp2 = urlquick.get(
        eval('URL_ROOT_%s' % DESIRED_LANGUAGE) + '/listing/program.%s/prepare/telecasts/10/%s' % (program_id, page))

    root = resp2.parse("ul", attrs={"class": "telecast-list js-listing__list"})

    for video_datas in root.iterfind(".//div[@class='telecast-list__content']"):
        video_title = video_datas.find(".//img").get('alt')
        video_image = video_datas.find(".//img").get('data-src')
        video_url = eval('URL_ROOT_%s' % DESIRED_LANGUAGE) + video_datas.find('.//a').get('href')
        video_plot = video_datas.find(".//p[@class='card__summary ']").text.strip()

        item = Listitem()
        item.label = video_title
        item.art['thumb'] = video_image
        item.info['plot'] = video_plot

        item.context.script(
            get_video_url,
            plugin.localize(LABELS['Download']),
            item_id=item_id,
            video_url=video_url,
            video_label=LABELS[item_id] + ' - ' + item.label,
            download_mode=True)

        item.set_callback(
            get_video_url,
            item_id=item_id,
            video_url=video_url)
        yield item

    yield Listitem.next_page(
        item_id=item_id,
        next_url=next_url,
        page=str(int(page) + 1))


@Route.register
def list_videos(plugin, item_id, page):

    resp = urlquick.get(
        eval('URL_ROOT_%s' % DESIRED_LANGUAGE) + '/listing/type.Videoclub.category.videos/noprepare/video-rows/10/%s' % (page))

    root = resp.parse("ul", attrs={"class": "media-rows js-listing__list"})

    for video_datas in root.iterfind(".//div[@class='media-rows__content']"):
        video_title = video_datas.find(".//img").get('alt')
        video_image = video_datas.find(".//img").get('data-src')
        video_url = eval('URL_ROOT_%s' % DESIRED_LANGUAGE) + video_datas.find('.//a').get('href')

        item = Listitem()
        item.label = video_title
        item.art['thumb'] = video_image

        item.context.script(
            get_video_url,
            plugin.localize(LABELS['Download']),
            item_id=item_id,
            video_url=video_url,
            video_label=LABELS[item_id] + ' - ' + item.label,
            download_mode=True)

        item.set_callback(
            get_video_url,
            item_id=item_id,
            video_url=video_url)
        yield item

    yield Listitem.next_page(
        item_id=item_id,
        page=str(int(page) + 1))


@Route.register
def list_videos_search(plugin, search_query, item_id, page):

    if DESIRED_LANGUAGE == 'FR':
        resp = urlquick.get(eval('URL_ROOT_%s' % DESIRED_LANGUAGE)  + '/recherche?search_api_views_fulltext=%s&page=%s' % (search_query, page))
    else:
        return False
    # resp = urlquick.get(URL_TIVI5MONDE_ROOT + '/recherche?search_api_views_fulltext=%s&page=%s' % (search_query, page))
    # root_soup = bs(resp.text, 'html.parser')
    # list_videos_datas = root_soup.find_all(
    #     'div', class_='row-vignette')

    # at_least_one_item = False
    # for video_datas in list_videos_datas:
    #     at_least_one_item = True
    #     video_title = video_datas.find('img').get('alt')
    #     video_image = video_datas.find('img').get('src')
    #     video_url = URL_TIVI5MONDE_ROOT + video_datas.find(
    #         'a').get('href')

    #     item = Listitem()
    #     item.label = video_title
    #     item.art['thumb'] = video_image

    #     item.context.script(
    #         get_video_url,
    #         plugin.localize(LABELS['Download']),
    #         item_id=item_id,
    #         video_url=video_url,
    #         video_label=LABELS[item_id] + ' - ' + item.label,
    #         download_mode=True)

    #     item.set_callback(
    #         get_video_url,
    #         item_id=item_id,
    #         video_url=video_url)
    #     yield item

    # if at_least_one_item:
    #     yield Listitem.next_page(
    #         item_id=item_id,
    #         search_query=search_query,
    #         page=str(int(page) + 1))
    # else:
    #     plugin.notify(plugin.localize(LABELS['No videos found']), '')
    #     yield False


@Resolver.register
def get_video_url(
        plugin, item_id, video_url, download_mode=False, video_label=None):

    resp = urlquick.get(video_url, max_age=-1)
    video_id = re.compile(
        r'youtube\.com\/embed\/(.*?)[\?\"]').findall(resp.text)[0]
    return resolver_proxy.get_stream_youtube(plugin, video_id, download_mode, video_label)


def live_entry(plugin, item_id, item_dict):
    return get_live_url(plugin, item_id, item_id.upper(), item_dict)


@Resolver.register
def get_live_url(plugin, item_id, video_id, item_dict):

    if DESIRED_LANGUAGE == 'EN':
        url_live = URL_LIVE_EN
        resp = urlquick.get(url_live, max_age=-1)
        return re.compile(
            r'file\: \'(.*?)\'').findall(resp.text)[0]
    elif DESIRED_LANGUAGE == 'AR':
        url_live = URL_LIVE_AR
        resp = urlquick.get(url_live, max_age=-1)
        return re.compile(
            r'file\'\: \'(.*?)\'').findall(resp.text)[0]
    elif DESIRED_LANGUAGE == 'FR':
        url_live = URL_LIVE_FR
        resp = urlquick.get(url_live, max_age=-1)
        return re.compile(
            r'file\: \"(.*?)\"').findall(resp.text)[0]
    elif DESIRED_LANGUAGE == 'ES':
        url_live = URL_LIVE_ES
        resp = urlquick.get(url_live, max_age=-1)
        live_id = re.compile(
            r'youtube\.com\/embed\/(.*?)\?').findall(resp.text)[0]
        return resolver_proxy.get_stream_youtube(plugin, live_id, False)
