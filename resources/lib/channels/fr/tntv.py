# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Joaopa
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import re
from builtins import str

from codequick import Listitem, Resolver, Route, Script
import urlquick
import json
import htmlement

from resources.lib import resolver_proxy, web_utils
from resources.lib.menu_utils import item_post_treatment


URL_ROOT = "https://www.tntv.pf/"
URL_API = URL_ROOT + 'tntv/wp-admin/admin-ajax.php'
URL_LIVE = URL_ROOT + "/direct"

GENERIC_HEADERS = {"User-Agent": web_utils.get_random_ua()}


@Route.register
def list_categories(plugin, item_id, **kwargs):
    resp = urlquick.get(URL_ROOT, headers=GENERIC_HEADERS, max_age=-1)
    root = resp.parse()
    duplicate = []

    for liste in root.iterfind(".//li"):
        for category in liste.iterfind(".//a"):
            if category.get('href') is not None:
                program = category.get('href')
                if 'category/programme' in program:
                    category_name = category.find(".//div[@class='tdb-menu-item-text']").text
                    if category_name not in duplicate:
                        duplicate.append(category_name)
                        item = Listitem()
                        item.label = category.find(".//div[@class='tdb-menu-item-text']").text
                        item.set_callback(list_subcategories, item_id=item_id, program=liste)
                        item_post_treatment(item)
                        yield item


@Route.register
def list_subcategories(plugin, item_id, program, **kwargs):
    submenu = program.find(".//ul[@class='sub-menu']")
    for menu in submenu.iterfind(".//li"):
        item = Listitem()
        menu_url = menu.find(".//a").get('href')
        if menu_url[0] == '/':
            menu_url = URL_ROOT + menu_url
        sub_page = urlquick.get(menu_url, headers=GENERIC_HEADERS).text
        picture_url = re.compile(r'property\=\"og\:image\" content\=\"(.*?)\"').findall(sub_page)[0]
        item.art['thumb'] = item.art['landscape'] = picture_url
        item.label = menu.find(".//div").text
        item.set_callback(list_videos, item_id=item_id, menu_url=menu_url, page='1')
        item_post_treatment(item, is_playable=True, is_downloadable=True)
        yield item


@Route.register
def list_videos(plugin, item_id, menu_url, page, **kwargs):
    API_HEADERS = {
        'User-Agent': 'Mozilla',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept-Encoding': 'gzip, deflate, br',
        'Origin': URL_ROOT,
        'Referer': menu_url,
    }

    data = {
        'action': 'td_ajax_block',
        'td_block_id': 'tdi_84',
        'td_column_number': '3',
        'td_current_page': page,
        'block_type': 'tdb_single_related',
        'td_magic_token': '07b55c8f0f',
        'td_filter_value': '',
        'td_user_action': ''
    }

    params = {
        'td_theme_name': 'Newspaper',
        'v': '12',
    }

    resp = urlquick.post(URL_API, headers=API_HEADERS, params=params, data=data, max_age=-1)
    json_parser = json.loads(resp.text)
    root = htmlement.fromstring(json_parser['td_data'])

    for video in root.iterfind(".//div[@class='tdb_module_related td_module_wrap td-animation-stack']"):
        item = Listitem()
        for video_pict in video.iterfind('.//span'):
            if video_pict.get('style') is not None:
                pict_url = re.compile(r"url\(\'(.*?)\'").findall(video_pict.get('style'))[0]
        item.art['thumb'] = item.art['landscape'] = pict_url
        video_desc = video.find(".//h3").find(".//a")
        item.label = video_desc.get('title')
        video_url = video_desc.get('href')
        item.set_callback(get_video_url, item_id=item_id, video_url=video_url)
        yield item

    if json_parser['td_hide_next'] is False:
        yield Listitem.next_page(item_id=item_id, menu_url=menu_url, page=str(int(page) + 1))


@Resolver.register
def get_video_url(plugin, item_id, video_url, **kwargs):
    resp = urlquick.get(video_url, headers=GENERIC_HEADERS, max_age=-1)
    root = resp.parse()

    for player in root.iterfind(".//frame"):
        if player.get('lazy') is None:
            video_id = re.compile(r'embed\/\?feature').findall(player.get('src'))
            if len(video_id) > 0:
                return resolver_proxy.get_stream_youtube(plugin, video_id)

    player = root.find('.//video-js')
    data_account = player.get('data-account')
    data_player = player.get('data-player')
    data_video_id = player.get('data-video-id')
    return resolver_proxy.get_brightcove_video_json(plugin, data_account, data_player, data_video_id)


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    resp = urlquick.get(URL_LIVE, headers={'User-Agent': web_utils.get_random_ua()}, max_age=-1)

    data_account_player = re.search('//players\.brightcove\.net/([0-9]+)/([A-Za-z0-9]+)_default/index\.html\?videoId=([0-9]+)', resp.text)
    data_account = data_account_player.group(1)
    data_player = data_account_player.group(2)
    data_video_id = data_account_player.group(3)

    return resolver_proxy.get_brightcove_video_json(plugin, data_account, data_player, data_video_id)
