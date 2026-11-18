# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Jeff2900
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import json
import re

from codequick import Listitem, Resolver, Route, Script
import urlquick

from resources.lib import resolver_proxy, web_utils
from resources.lib.menu_utils import item_post_treatment

URL_ROOT = 'https://t18.fr'
EMBEDER_URL = 'https://www.dailymotion.com/video/%s'
GENERIC_HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36'}


@Route.register
def list_categories(plugin, item_id, **kwargs):
    """
    Build categories listing
    - Nos documentaires et magazines
    - Nos films
    - ...
    """
    resp = urlquick.get(URL_ROOT, headers=GENERIC_HEADERS, max_age=-1)
    root = resp.parse()

    for datas in root.iterfind(".//li[@class='menu__item']"):
        category_title = datas.findtext('.//span[@class="button__text"]')
        category_url = datas.find('.//a').get('href')
        if 'http' not in category_url:
            category_url = URL_ROOT + category_url

        item = Listitem()
        item.label = category_title
        item.set_callback(list_programs,
                          url=category_url)
        item_post_treatment(item)
        yield item


@Route.register(autosort=False)
def list_programs(plugin, url, **kwargs):
    """
    Build programs listing
    - Journal de 20H
    - Cash investigation
    ...
    """
    resp = urlquick.get(url, headers=GENERIC_HEADERS)
    root = resp.parse()
    at_least_one_item = False

    for datas in root.iterfind(".//li[@class='products-list__item']"):
        program_title = datas.findtext(".//h3[@class='product-card__title']")

        program_url = datas.find('.//a').get('href')
        program_image = datas.find('.//img').get('data-src')
        if 'http' not in program_url:
            program_url = URL_ROOT + program_url

        if program_title:
            at_least_one_item = True
            item = Listitem()
            item.label = program_title
            item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = program_image
            item.set_callback(list_videos,
                              url=program_url)
            item_post_treatment(item)
            yield item

    # No item found
    if not at_least_one_item:
        item = Listitem()
        item.label = Script.localize(30896)
        item_post_treatment(item)
        yield item


@Route.register(autosort=False)
def list_videos(plugin, url, **kwargs):
    """
    Build videos listing
    - Episodes 1
    - Episodes 2
    ...
    """
    resp = urlquick.get(url, headers=GENERIC_HEADERS, max_age=-1)

    data_pagination_url = re.compile(r'data-pagination-url=\"(.*?)\"').findall(resp.text)

    if data_pagination_url:
        data_pagination_url = data_pagination_url[0]
        data_pagination_pages_count = re.compile(r'data-pagination-pages-count=\"(.*?)\"').findall(resp.text)[0]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        }

        i = 0
        while i < int(data_pagination_pages_count):
            i += 1
            params = {
                'p': i,
            }
            resp = urlquick.get(URL_ROOT + data_pagination_url, params=params, headers=headers, max_age=-1)
            json_parser = json.loads(resp.text)

            for datas in json_parser:
                video_label = datas.get('title')
                video_url = datas.get('url')
                video_desc = datas.get('summary')
                video_image = datas.get('imageUrl')
                video_date = datas.get('broadcastedAt')
                if video_date is not None:
                    video_date = video_date.split('T')[0]

                video_duration = datas.get('duration')
                Hrs_h = Hrs_m = None
                if video_duration is not None:
                    if 'H' in video_duration:
                        Hrs_h = re.compile(r'(\d+)H').findall(video_duration)
                    if 'M' in video_duration:
                        Hrs_m = re.compile(r'(\d+)M').findall(video_duration)

                    if Hrs_h:
                        if Hrs_m:
                            duration = int(Hrs_m[-1]) + int(60) * int(Hrs_h[0])
                        else:
                            duration = int(60) * int(Hrs_h[0])
                    elif Hrs_m:
                        duration = int(Hrs_m[-1])
                    else:
                        duration = None

                item = Listitem()
                item.label = video_label
                item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = video_image
                if video_desc:
                    item.info['plot'] = video_desc
                if video_date:
                    item.info.date(video_date, '%Y-%m-%d')
                if duration:
                    item.info['duration'] = duration
                item.set_callback(get_video_url,
                                  video_url=video_url)
                item_post_treatment(item)
                yield item
    else:
        root = resp.parse()
        video_title = root.findtext(".//title")
        video_desc = root.findtext(".//p[@class='about-card__details-summary']")

        for datas in root.iterfind(".//figure[@class='figure about-card__figure']"):
            video_image = datas.find('.//img').get('data-src')

        item = Listitem()
        item.label = video_title
        item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = video_image
        if video_desc:
            item.info['plot'] = video_desc
        item.set_callback(get_video_url,
                          video_url=url)
        item_post_treatment(item)
        yield item


@Resolver.register
def get_video_url(plugin, video_url):
    resp = urlquick.get(video_url, headers=GENERIC_HEADERS, max_age=-1)

    video_id = re.compile(r'data-dailymotion-video-id=\"(.*?)\"').findall(resp.text)[0]
    return resolver_proxy.get_stream_dailymotion(plugin, video_id, download_mode=False, embeder=video_url)


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    try:
        resp = urlquick.get(URL_ROOT + '/direct', headers=GENERIC_HEADERS, max_age=-1)
        live_id = re.compile(r'"https://geo.dailymotion.com/player.html\?video=(.*?)[\?\"]').findall(resp.text)[0]
        return resolver_proxy.get_stream_dailymotion(plugin, live_id, download_mode=False, embeder=EMBEDER_URL % live_id)

    except Exception:
        return resolver_proxy.get_stream_dailymotion(plugin, 'x9jhhyc', False, embeder=EMBEDER_URL % 'x9jhhyc')
