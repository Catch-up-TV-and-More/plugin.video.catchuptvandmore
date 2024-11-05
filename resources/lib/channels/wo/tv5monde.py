# -*- coding: utf-8 -*-
# Copyright: (c) 2017, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import json
import re
from builtins import str

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import urlquick
# noinspection PyUnresolvedReferences
from codequick import Listitem, Resolver, Route, Script
from resources.lib import download, web_utils, resolver_proxy
from resources.lib.menu_utils import item_post_treatment

# TODO Rework filter for all videos

URL_TV5MONDE_LIVE = 'http://live.tv5monde.com/'

URL_TV5MONDE_ROOT = 'https://www.tv5monde.com'

URL_TV5MONDE_API = 'https://api.tv5monde.com/player/asset/%s/resolve?condenseKS=true'
M3U8_NOT_FBS = 'https://ott.tv5monde.com/Content/HLS/Live/channel(europe)/variant.m3u8'

LIST_LIVE_TV5MONDE = {'tv5mondefbs': 'fbs', 'tv5mondeinfo': 'infoplus'}

LIVETYPE = {
    "FBS": "0",
    "NOT_FBS": "1"
}

HEADERS_GENERIC = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}


@Route.register
def list_categories(plugin, item_id, **kwargs):
    """
    Build categories listing
    - Tous les programmes
    - Séries
    - Informations
    - ...
    """
    resp = urlquick.get(URL_TV5MONDE_ROOT + '/tv',
                        headers=HEADERS_GENERIC,
                        max_age=-1)

    root = resp.parse("footer", attrs={"role": "footer-content"})
    for category_datas in root.iterfind(".//li"):
        category_title = category_datas.find('.//a').text.strip()
        category_url = URL_TV5MONDE_ROOT + category_datas.find('.//a').get(
            'href')

        item = Listitem()
        item.label = category_title
        item.set_callback(list_programs,
                          item_id=item_id,
                          category_url=category_url,
                          page='1')
        item_post_treatment(item)
        yield item


@Route.register
def list_programs(plugin, item_id, category_url, page, **kwargs):
    """
    Build programs listing
    - Les feux de l'amour
    - ...
    """
    resp = urlquick.get(category_url + '?page=%s' % page,
                        headers=HEADERS_GENERIC,
                        max_age=-1)

    root = resp.parse("main", attrs={"role": "main-content"})
    for program_datas in root.iterfind(".//li"):
        if 'http' in program_datas.find('.//a').get('href'):
            program_url = program_datas.find('.//a').get('href')
        else:
            program_url = URL_TV5MONDE_ROOT + program_datas.find('.//a').get('href')
        try:
            if 'http' in program_datas.find('.//img').get('src'):
                program_title = program_datas.find('.//img').get('alt')
                program_image = program_datas.find('.//img').get('src')
            else:
                program_title = program_datas.find('.//img').get('alt')
                program_image = URL_TV5MONDE_ROOT + program_datas.find('.//img').get('src')
        except Exception:
            continue

        item = Listitem()
        item.label = program_title
        item.art['thumb'] = item.art['landscape'] = program_image
        item.set_callback(list_videos,
                          item_id=item_id,
                          program_url=program_url,
                          page='1')
        item_post_treatment(item)
        yield item

    yield Listitem.next_page(item_id=item_id,
                             category_url=category_url,
                             page=str(int(page) + 1))


@Route.register
def list_videos(plugin, item_id, program_url, page, **kwargs):
    resp = urlquick.get(program_url + '?page=%s' % page,
                        headers=HEADERS_GENERIC,
                        max_age=-1)
    root = resp.parse("main", attrs={"role": "main-content"})
    if root.findall(".//div[@class='video-wrapper']"):
        video_title = root.find(".//h1").text.strip()
        item = Listitem()
        item.label = video_title
        item.set_callback(get_video_url,
                          item_id=item_id,
                          video_url=program_url)
        yield item
        return

    for video_datas in root.iterfind(".//li"):
        if 'http' in video_datas.find('.//a').get('href'):
            video_url = video_datas.find('.//a').get('href')
        else:
            video_url = URL_TV5MONDE_ROOT + video_datas.find('.//a').get('href')
        try:
            if 'http' in video_datas.find('.//img').get('src'):
                video_title = video_datas.find('.//img').get('alt')
                video_image = video_datas.find('.//img').get('src')
            else:
                video_title = video_datas.find('.//img').get('alt')
                video_image = URL_TV5MONDE_ROOT + video_datas.find('.//img').get('src')
        except Exception:
            continue

        item = Listitem()
        item.label = video_title
        item.art['thumb'] = item.art['landscape'] = video_image

        item.set_callback(get_video_url,
                          item_id=item_id,
                          video_url=video_url)
        item_post_treatment(item, is_playable=True, is_downloadable=True)
        yield item

    yield Listitem.next_page(item_id=item_id,
                             program_url=program_url,
                             page=str(int(page) + 1))


@Route.register
def list_videos_category(plugin, item_id, page, **kwargs):
    resp = urlquick.get(URL_TV5MONDE_ROOT +
                        '/toutes-les-videos?page=%s' % page,
                        headers={'User-Agent': web_utils.get_random_ua()})
    root = resp.parse()

    for video_datas in root.iterfind(".//div[@class='bloc-episode-content']"):
        if video_datas.find('.//h3') is not None:
            video_title = video_datas.find('.//h2').text.strip() + ' - ' + video_datas.find('.//h3').text.strip()
        else:
            video_title = video_datas.find('.//h2').text.strip()
        if 'http' in video_datas.find('.//img').get('src'):
            video_image = video_datas.find('.//img').get('src')
        else:
            video_image = URL_TV5MONDE_ROOT + video_datas.find('.//img').get(
                'src')
        video_url = URL_TV5MONDE_ROOT + video_datas.find('.//a').get('href')

        item = Listitem()
        item.label = video_title
        item.art['thumb'] = item.art['landscape'] = video_image

        item.set_callback(get_video_url,
                          item_id=item_id,
                          video_url=video_url)
        item_post_treatment(item, is_playable=True, is_downloadable=True)
        yield item

    yield Listitem.next_page(item_id=item_id,
                             page=str(int(page) + 1))


@Resolver.register
def get_video_url(plugin,
                  item_id,
                  video_url,
                  download_mode=False,
                  **kwargs):
    resp = urlquick.get(video_url,
                        headers=HEADERS_GENERIC,
                        max_age=-1)
    video_json = re.compile('data-broadcast=\'(.*?)\'').findall(resp.text)[0]
    json_parser = json.loads(video_json)
    try:
        api_url = json_parser["files"][0]["url"]
        token = json_parser["files"][0]["token"]
    except Exception:
        api_url = json_parser[0]["url"]
        token = json_parser[0]["token"]

    api_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "authorization": "Bearer %s" % token,
    }
    resp = urlquick.get(URL_TV5MONDE_API % api_url,
                        headers=api_headers,
                        max_age=-1)

    json_parser = resp.json()
    license_key = None
    license_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
        'Content-Type': 'application/octet-stream'
    }
    for video_datas in json_parser:
        if 'dash' in video_datas["type"]:
            final_video_url = video_datas["url"]
            if 'drm' in video_datas:
                license_url = video_datas["drm"]["keySystems"]["widevine"]["license"]
                license_config = {  # for Python < v3.7 you should use OrderedDict to keep order
                    'license_server_url': license_url,
                    'headers': urlencode(license_headers),
                    'post_data': 'R{SSM}',
                    'response_data': 'R'
                }
                license_key = '|'.join(license_config.values())
                continue

    if final_video_url is None:
        final_video_url = json_parser[0]["url"]
        return final_video_url

    return resolver_proxy.get_stream_with_quality(plugin,
                                                  video_url=final_video_url,
                                                  manifest_type='mpd',
                                                  license_url=license_key)


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    region = Script.setting['tv5monde.region']
    if region == LIVETYPE['NOT_FBS']:
        return resolver_proxy.get_stream_with_quality(plugin, video_url=M3U8_NOT_FBS, manifest_type="hls")

    live_id = ''
    for channel_name, live_id_value in list(LIST_LIVE_TV5MONDE.items()):
        if item_id == channel_name:
            live_id = live_id_value
    resp = urlquick.get(URL_TV5MONDE_LIVE + '%s.html' % live_id,
                        headers=HEADERS_GENERIC,
                        max_age=-1)
    live_json = re.compile(r'data-broadcast=\'(.*?)\'').findall(resp.text)[0]
    json_parser = json.loads(live_json)

    return resolver_proxy.get_stream_with_quality(plugin, video_url=json_parser[0]["url"], manifest_type="hls")
