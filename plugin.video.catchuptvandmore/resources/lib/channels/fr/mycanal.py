# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2017 SylvainCecchetto

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


from resources.lib import web_utils
from resources.lib import resolver_proxy
from resources.lib import download
from resources.lib.menu_utils import item_post_treatment
from resources.lib.kodi_utils import get_kodi_version, get_selected_item_art, get_selected_item_label, get_selected_item_info
from resources.lib.addon_utils import get_item_media_path

import inputstreamhelper
import re
import json
import urlquick
from kodi_six import xbmc
from kodi_six import xbmcgui
import requests
# Working for Python 2/3
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

# TO DO
# Wait Kodi 18 to use live with DRM

# URL :
URL_ROOT_SITE = 'https://www.mycanal.fr'
# Channel

# Replay channel :
URL_REPLAY = URL_ROOT_SITE + '/chaines/%s'
# Channel name

URL_TOKEN = 'https://pass-api-v2.canal-plus.com/services/apipublique/createToken'

URL_VIDEO_DATAS = 'https://secure-gen-hapi.canal-plus.com/conso/playset?contentId=%s'

URL_STREAM_DATAS = 'https://secure-gen-hapi.canal-plus.com/conso/view'

URL_DEVICE_ID = 'https://pass.canal-plus.com/service/HelloJSON.php'

# TODO
URL_LICENCE_DRM = '[license-server url]|[Header]|[Post-Data]|[Response]'
# com.widevine.alpha
# license_key must be a string template with 4 | separated fields: [license-server url]|[Header]|[Post-Data]|[Response] in which [license-server url] allows B{SSM} placeholder and [Post-Data] allows [b/B/R]{SSM} and [b/B/R]{SID} placeholders to transport the widevine challenge and if required the DRM SessionId in base64NonURLencoded, Base64URLencoded or Raw format.
# [Response] can be a.) empty or R to specify that the response payload of the license request is binary format, b.) B if the response payload is base64 encoded or c.) J[licensetoken] if the license key data is located in a JSON struct returned in the response payload.
# inputstream.adaptive searches for the key [licensetoken] and handles the value as base64 encoded data.

# Dailymotion Id get from these pages below
# - http://www.dailymotion.com/cstar
# - http://www.dailymotion.com/canalplus
# - http://www.dailymotion.com/C8TV
LIVE_DAILYMOTION_ID = {
    'c8': 'x5gv5rr',
    'cstar': 'x5gv5v0',
    'canalplus': 'x5gv6be'
}


@Route.register
def mycanal_root(plugin, **kwargs):

    # (item_id, label, thumb, fanart)
    channels = [
        ('canalplus-en-clair', 'Canal +', 'canalplus.png', 'canalplus_fanart.jpg'),
        ('c8', 'C8', 'c8.png', 'c8_fanart.jpg'),
        ('cstar', 'CStar', 'cstar.png', 'cstar_fanart.jpg'),
        ('seasons', 'Seasons', 'seasons.png', 'seasons_fanart.jpg'),
        ('comedie', 'Comédie +', 'comedie.png', 'comedie_fanart.jpg'),
        ('les-chaines-planete', 'Les chaînes planètes +', 'leschainesplanete.png', 'leschainesplanete_fanart.jpg'),
        ('golfplus', 'Golf +', 'golfplus.png', 'golfplus_fanart.jpg'),
        ('cineplus-en-clair', 'Ciné +', 'cineplus.png', 'cineplus_fanart.jpg'),
        ('infosportplus', 'INFOSPORT+', 'infosportplus.png', 'infosportplus_fanart.jpg'),
        ('polar-plus', 'Polar+', 'polarplus.png', 'polarplus_fanart.jpg'),
        ('clique-tv', 'Clique TV', 'cliquetv.png', 'cliquetv_fanart.jpg'),
        ('piwi', 'Piwi +', 'piwiplus.png', 'piwiplus_fanart.jpg'),
        ('teletoon', 'TéléToon +', 'teletoonplus.png', 'teletoonplus_fanart.jpg'),
    ]

    for channel_infos in channels:
        item = Listitem()
        item.label = channel_infos[1]
        item.art["thumb"] = get_item_media_path('channels/fr/' + channel_infos[2])
        item.art["fanart"] = get_item_media_path('channels/fr/' + channel_infos[3])
        item.set_callback(list_categories, channel_infos[0])
        item_post_treatment(item)
        yield item


@Route.register
def list_categories(plugin, item_id, **kwargs):
    """
    Build categories listing
    - Tous les programmes
    - Séries
    - Informations
    - ...
    """

    resp = urlquick.get(URL_REPLAY % item_id)
    json_replay = re.compile(
        r'window.__data\=(.*?)\; window.app_config').findall(resp.text)[0]
    json_parser = json.loads(json_replay)

    for category in json_parser["templates"]["landing"]["strates"]:
        if category["type"] == "carrousel":
            title = category['context']['context_page_title']
            key_value = category['key']
            item = Listitem()
            item.label = title
            item.set_callback(
                list_contents, item_id=item_id, key_value=key_value)
            item_post_treatment(item)
            yield item
        elif category["type"] == "contentRow":
            if 'title' in category:
                title = category['title']
            else:
                title = json_parser["page"]["displayName"]
            key_value = category['key']
            item = Listitem()
            item.label = title
            item.set_callback(
                list_contents, item_id=item_id, key_value=key_value)
            item_post_treatment(item)
            yield item


@Route.register
def list_contents(plugin, item_id, key_value, **kwargs):

    resp = urlquick.get(URL_REPLAY % item_id)
    json_replay = re.compile(
        r'window.__data\=(.*?)\; window.app_config').findall(resp.text)[0]
    json_parser = json.loads(json_replay)

    for category in json_parser["templates"]["landing"]["strates"]:
        if category['key'] == key_value:
            for content in category["contents"]:
                if content["type"] != 'article':
                    content_title = content["onClick"]["displayName"]
                    if 'http' in content["URLImageOptimizedRegular"]:
                        content_image = content["URLImageOptimizedRegular"]
                    else:
                        content_image = content["URLImage"]
                    content_url = content["onClick"]["URLPage"]

                    item = Listitem()
                    item.label = content_title
                    item.art['thumb'] = item.art['landscape'] = content_image
                    item.set_callback(
                        list_programs,
                        item_id=item_id,
                        next_url=content_url)
                    item_post_treatment(item)
                    yield item


@Route.register
def list_programs(plugin, item_id, next_url, **kwargs):

    resp = urlquick.get(next_url)
    json_parser = json.loads(resp.text)

    if 'strates' in json_parser:

        program_title = json_parser['currentPage']['displayName']

        for strate in json_parser["strates"]:
            if strate["type"] == "contentRow" or strate["type"] == "contentGrid":
                strate_title = program_title + ' - ' + strate["title"]

                item = Listitem()
                item.label = strate_title

                item.set_callback(
                    list_sub_programs,
                    item_id=item_id,
                    next_url=next_url,
                    strate_title=strate_title)
                item_post_treatment(item)
                yield item

    elif 'episodes' in json_parser:

        program_title = json_parser['currentPage']['displayName']

        for video_datas in json_parser["episodes"]['contents']:
            video_title = program_title + ' - ' + video_datas['title']
            video_image = video_datas['URLImage']
            video_plot = ''
            if 'summary' in video_datas:
                video_plot = video_datas['summary']
            tokencms_value = ''
            if 'contentAvailability' in video_datas:
                video_url = video_datas["contentAvailability"]["availabilities"]["stream"]["URLMedias"]
                # find tokencms_value
            else:
                video_url = video_datas["URLMedias"]

            item = Listitem()
            item.label = video_title
            item.art['thumb'] = item.art['landscape'] = video_image
            item.info['plot'] = video_plot

            item.set_callback(
                get_video_url,
                item_id=item_id,
                next_url=video_url,
                tokencms_value=tokencms_value)
            item_post_treatment(item, is_playable=True, is_downloadable=True)
            yield item

        if json_parser["episodes"]["paging"]["hasNextPage"]:
            yield Listitem.next_page(item_id=item_id,
                                     next_url=json_parser["episodes"]["paging"]["URLPage"])

    elif 'detail' in json_parser:

        if 'seasons' in json_parser['detail']:
            for seasons_datas in json_parser['detail']['seasons']:
                if 'seasonNumber' in seasons_datas:
                    season_title = seasons_datas['onClick']['displayName'] + \
                        ' (Saison ' + str(seasons_datas["seasonNumber"]) + ')'
                else:
                    season_title = seasons_datas['onClick']['displayName']
                season_url = seasons_datas['onClick']['URLPage']

                item = Listitem()
                item.label = season_title
                item.set_callback(
                    list_videos, item_id=item_id, next_url=season_url)
                item_post_treatment(item)
                yield item

        else:
            # Case just one video
            program_title = json_parser['currentPage']['displayName']
            video_datas = json_parser['detail']['informations']

            if 'subtitle' in video_datas:
                video_title = program_title + ' - ' + video_datas['title'] + ' - ' + video_datas['subtitle']
            else:
                video_title = program_title + ' - ' + video_datas['title']
            video_image = video_datas['URLImage']
            video_plot = ''
            if 'summary' in video_datas:
                video_plot = video_datas['summary']
            tokencms_value = ''
            if 'contentAvailability' in video_datas:
                video_url = video_datas["contentAvailability"]["availabilities"]["stream"]["URLMedias"]
                # find tokencms_value
            else:
                video_url = video_datas["URLMedias"]

            item = Listitem()
            item.label = video_title
            item.art['thumb'] = item.art['landscape'] = video_image
            item.info['plot'] = video_plot

            item.set_callback(
                get_video_url,
                item_id=item_id,
                next_url=video_url,
                tokencms_value=tokencms_value)
            item_post_treatment(item, is_playable=True, is_downloadable=True)
            yield item

    elif 'contents' in json_parser:

        for content_datas in json_parser['contents']:
            if content_datas["type"] != 'article':
                if 'subtitle' in content_datas:
                    content_title = content_datas['title'] + \
                        ' - ' + content_datas['subtitle']
                else:
                    content_title = content_datas['title']
                content_image = content_datas['URLImage']
                content_url = content_datas['onClick']['URLPage']

                item = Listitem()
                item.label = content_title
                item.art['thumb'] = item.art['landscape'] = content_image

                item.set_callback(
                    list_videos,
                    item_id=item_id,
                    next_url=content_url)
                item_post_treatment(item)
                yield item


@Route.register
def list_sub_programs(plugin, item_id, next_url, strate_title, **kwargs):

    resp = urlquick.get(next_url)
    json_parser = json.loads(resp.text)

    if 'strates' in json_parser:

        for strate in json_parser["strates"]:
            if strate["type"] == "contentRow" or strate["type"] == "contentGrid":
                if strate["title"] in strate_title:
                    for content_datas in strate['contents']:
                        if content_datas["type"] != 'article':
                            if 'subtitle' in content_datas:
                                content_title = content_datas['title'] + \
                                    ' - ' + content_datas['subtitle']
                            else:
                                content_title = content_datas['title']
                            content_image = content_datas['URLImage']
                            content_url = content_datas['onClick']['URLPage']

                            item = Listitem()
                            item.label = content_title
                            item.art['thumb'] = item.art['landscape'] = content_image

                            item.set_callback(
                                list_programs,
                                item_id=item_id,
                                next_url=content_url)
                            item_post_treatment(item)
                            yield item


@Route.register
def list_videos(plugin, item_id, next_url, **kwargs):

    resp = urlquick.get(next_url)
    json_parser = json.loads(resp.text)

    program_title = json_parser['currentPage']['displayName']

    for video_datas in json_parser["episodes"]['contents']:
        video_title = program_title + ' - ' + video_datas['title']
        video_image = video_datas['URLImage']
        video_plot = ''
        if 'summary' in video_datas:
            video_plot = video_datas['summary']
        tokencms_value = ''
        if 'contentAvailability' in video_datas:
            video_url = video_datas["contentAvailability"]["availabilities"]["stream"]["URLMedias"]
            # find tokencms_value
        else:
            video_url = video_datas["URLMedias"]

        item = Listitem()
        item.label = video_title
        item.art['thumb'] = item.art['landscape'] = video_image
        item.info['plot'] = video_plot

        item.set_callback(
            get_video_url,
            item_id=item_id,
            next_url=video_url,
            tokencms_value=tokencms_value)
        item_post_treatment(item, is_playable=True, is_downloadable=True)
        yield item

    if json_parser["episodes"]["paging"]["hasNextPage"]:
        yield Listitem.next_page(item_id=item_id,
                                 next_url=json_parser["episodes"]["paging"]["URLPage"])


@Resolver.register
def get_video_url(plugin,
                  item_id,
                  next_url,
                  tokencms_value,
                  download_mode=False,
                  **kwargs):

    if 'tokenCMS' in next_url:
        # TODO get TOKENCMS_VALUE
        return False
    else:
        resp = urlquick.get(
            next_url, headers={'User-Agent': web_utils.get_random_ua()}, max_age=-1)
        json_parser = json.loads(resp.text)

        return json_parser["detail"]["informations"]["playsets"]["available"][0]["videoURL"]


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    return resolver_proxy.get_stream_dailymotion(
        plugin, LIVE_DAILYMOTION_ID[item_id], False)
