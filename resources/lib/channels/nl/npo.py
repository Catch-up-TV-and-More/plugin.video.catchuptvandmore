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
import resources.lib.cq_utils as cqu
from resources.lib.listitem_utils import item_post_treatment, item2dict

import htmlement
import inputstreamhelper
import json
import re
import urlquick
import xbmc
import xbmcgui

# TO DO
# More Programs, More Videos

URL_ROOT = 'https://www.npostart.nl'

URL_LIVE_ID = URL_ROOT + '/live/%s'
# Live Id
URL_TOKEN_ID = URL_ROOT + '/player/%s'
# Id video
URL_TOKEN_API = URL_ROOT + '/api/token'
URL_STREAM = 'https://start-player.npo.nl/video/%s/streams?profile=dash-widevine&quality=npo&tokenId=%s&streamType=broadcast&mobile=0&ios=0&isChromecast=0'
# Id video, tokenId
URL_SUBTITLE = 'https://rs.poms.omroep.nl/v1/api/subtitles/%s'
# Id Video

URL_PROGRAMS = URL_ROOT + '/programmas?az=%s&genreId='
# Page
URL_PROGRAMS_API = URL_ROOT + '/media/series?page=%s&dateFrom=2014-01-01&az=%s&tileMapping=normal&tileType=teaser&pageType=catalogue'
# Page, Letter

LETTER_LIST = [
    "0-9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
]


def replay_entry(plugin, item_id, **kwargs):
    """
    First executed function after replay_bridge
    """
    return list_letters(plugin, item_id)


@Route.register
def list_letters(plugin, item_id, **kwargs):
    """
    Build programs listing
    - Les feux de l'amour
    - ...
    """
    for letter_value in LETTER_LIST:
        item = Listitem()
        item.label = letter_value
        item.set_callback(
            list_programs,
            item_id=item_id,
            letter_value=letter_value,
            page='1')
        item_post_treatment(item)
        yield item


@Route.register
def list_programs(plugin, item_id, letter_value, page, **kwargs):

    if int(page) > 1:
        # TODO Return 404 ... (maybe just use this implementation if we find a way to make it work)
        headers = {
            'referer':
            'https://www.npostart.nl/programmas?az=%s&genreId=' % letter_value
        }
        resp = urlquick.get(
            URL_PROGRAMS_API % (page, letter_value), headers=headers)
        json_parser = json.loads(resp.text)

        for program_datas_html in json_parser["tiles"]:

            parser = htmlement.HTMLement()
            parser.feed(program_datas_html)
            root = parser.close()

            program_title = root.find(".//h2").text
            program_image = root.find(".//img").get("data-src")
            program_url = root.find(".//a").get("href")

            item = Listitem()
            item.label = program_title
            item.art['thumb'] = program_image
            item.set_callback(
                list_videos,
                item_id=item_id,
                program_url=program_url,
                page='1')
            item_post_treatment(item)
            yield item

    else:

        resp = urlquick.get(URL_PROGRAMS % letter_value)
        root = resp.parse()

        for program_datas in root.iterfind(
                ".//div[@class='npo-ankeiler-tile-container npo-ankeiler-tile-weblink npo-tile']"
        ):

            program_title = program_datas.find(".//h2").text
            program_image = program_datas.find(".//img").get("data-src")
            program_url = program_datas.find(".//a").get("href")

            item = Listitem()
            item.label = program_title
            item.art['thumb'] = program_image
            item.set_callback(
                list_videos,
                item_id=item_id,
                program_url=program_url,
                page='1')
            item_post_treatment(item)
            yield item

    # More programs...
    yield Listitem.next_page(
        item_id=item_id, letter_value=letter_value, page=str(int(page) + 1))


@Route.register
def list_videos(plugin, item_id, program_url, page, **kwargs):

    resp = urlquick.get(program_url)
    root = resp.parse()

    if root.find(".//header[@class='npo-header-episode']") is not None:
        video_datas = root.find(".//header[@class='npo-header-episode']")
        video_title = video_datas.find(".//h2").text
        video_image = video_datas.find(".//div[@class='header-fallback']").get(
            'style')
        video_image = re.compile(r'url\(\"(.*?)\"').findall(video_image)[0]
        video_plot = video_datas.find(".//p[@class='summary_short']").text
        video_id = video_datas.get('data-episode')

        item = Listitem()
        item.label = video_title
        item.art['thumb'] = video_image
        item.info['plot'] = video_plot

        item.set_callback(
            get_video_url,
            item_id=item_id,
            video_label=LABELS[item_id] + ' - ' + item.label,
            video_id=video_id,
            item_dict=item2dict(item))
        item_post_treatment(item, is_playable=True, is_downloadable=False)
        yield item
    else:
        for video_datas in root.iterfind(
                ".//div[@class='npo-asset-tile-container npo-tile   ']"):

            video_title = video_datas.find(".//h2").text
            video_image = video_datas.find(".//img").get('data-src')
            video_plot = video_datas.find(".//p").text
            video_id = video_datas.get('data-id')

            item = Listitem()
            item.label = video_title
            item.art['thumb'] = video_image
            item.info['plot'] = video_plot

            item.set_callback(
                get_video_url,
                item_id=item_id,
                video_label=LABELS[item_id] + ' - ' + item.label,
                video_id=video_id,
                item_dict=item2dict(item))
            item_post_treatment(item, is_playable=True, is_downloadable=False)
            yield item
    # TODO add more videos


@Resolver.register
def get_video_url(plugin,
                  item_id,
                  video_id,
                  item_dict,
                  download_mode=False,
                  video_label=None,
                  **kwargs):

    if cqu.get_kodi_version() < 18:
        xbmcgui.Dialog().ok('Info', plugin.localize(30602))
        return False

    is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
    if not is_helper.check_inputstream():
        return False

    headers = {'X-Requested-With': 'XMLHttpRequest'}

    resp_token = urlquick.get(URL_TOKEN_API, headers=headers, max_age=-1)
    session_token = resp_token.cookies['npo_session']

    json_parser_token = json.loads(resp_token.text)
    api_token = json_parser_token['token']

    # Build PAYLOAD
    payload = {"_token": api_token}

    cookies = {"npo_session": session_token}

    resp2 = urlquick.post(
        URL_TOKEN_ID % video_id, cookies=cookies, data=payload, max_age=-1)
    json_parser = json.loads(resp2.text)
    token_id = json_parser['token']

    resp3 = urlquick.get(URL_STREAM % (video_id, token_id), max_age=-1)
    json_parser2 = json.loads(resp3.text)

    if "html" in json_parser2 and "Dit programma mag niet bekeken worden vanaf jouw locatie (33)." in json_parser2["html"]:
        plugin.notify('ERROR', plugin.localize(30713))
        return False
    elif "html" in json_parser2 and "Dit programma is niet (meer) beschikbaar (15)." in json_parser2["html"]:
        plugin.notify('ERROR', plugin.localize(30710))
        return False

    licence_url = json_parser2["stream"]["keySystemOptions"][0]["options"][
        "licenseUrl"]
    licence_url_header = json_parser2["stream"]["keySystemOptions"][0][
        "options"]["httpRequestHeaders"]
    xcdata_value = licence_url_header["x-custom-data"]

    item = Listitem()
    item.path = json_parser2["stream"]["src"]
    item.label = item_dict['label']
    item.info.update(item_dict['info'])
    item.art.update(item_dict['art'])
    if plugin.setting.get_boolean('active_subtitle'):
        item.subtitles.append(URL_SUBTITLE % video_id)
    item.property['inputstreamaddon'] = 'inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property['inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property[
        'inputstream.adaptive.license_key'] = licence_url + '|Content-Type=&User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3041.0 Safari/537.36&x-custom-data=%s|R{SSM}|' % xcdata_value

    return item


def live_entry(plugin, item_id, item_dict, **kwargs):
    return get_live_url(plugin, item_id, item_id.upper(), item_dict)


@Resolver.register
def get_live_url(plugin, item_id, video_id, item_dict, **kwargs):

    if cqu.get_kodi_version() < 18:
        xbmcgui.Dialog().ok('Info', plugin.localize(30602))
        return False

    is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
    if not is_helper.check_inputstream():
        return False

    headers = {'X-Requested-With': 'XMLHttpRequest'}

    resp_token = urlquick.get(URL_TOKEN_API, headers=headers, max_age=-1)
    session_token = resp_token.cookies['npo_session']

    json_parser_token = json.loads(resp_token.text)
    api_token = json_parser_token['token']

    resp = urlquick.get(URL_LIVE_ID % item_id, max_age=-1)

    video_id = re.compile(r'\"iframe\-(.*?)\"').findall(resp.text)[0]

    # Build PAYLOAD
    payload = {"_token": api_token}

    cookies = {"npo_session": session_token}

    resp2 = urlquick.post(URL_TOKEN_ID % video_id,
                          cookies=cookies,
                          data=payload,
                          max_age=-1)
    json_parser = json.loads(resp2.text)
    token_id = json_parser['token']

    resp3 = urlquick.get(URL_STREAM % (video_id, token_id), max_age=-1)
    json_parser2 = json.loads(resp3.text)

    if "html" in json_parser2 and "Vanwege uitzendrechten is het niet mogelijk om deze uitzending buiten Nederland te bekijken." in json_parser2[
            "html"]:
        plugin.notify('ERROR', plugin.localize(30713))
        return False

    licence_url = json_parser2["stream"]["keySystemOptions"][0]["options"][
        "licenseUrl"]
    licence_url_header = json_parser2["stream"]["keySystemOptions"][0][
        "options"]["httpRequestHeaders"]
    xcdata_value = licence_url_header["x-custom-data"]

    item = Listitem()
    item.path = json_parser2["stream"]["src"]
    if item_dict:
        if 'label' in item_dict:
            item.label = item_dict['label']
        if 'info' in item_dict:
            item.info.update(item_dict['info'])
        if 'art' in item_dict:
            item.art.update(item_dict['art'])
    else:
        item.label = LABELS[item_id]
        item.art["thumb"] = ""
        item.art["icon"] = ""
        item.art["fanart"] = ""
        item.info["plot"] = LABELS[item_id]
    if plugin.setting.get_boolean('active_subtitle'):
        item.subtitles.append(URL_SUBTITLE % video_id)
    item.property['inputstreamaddon'] = 'inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property['inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property[
        'inputstream.adaptive.license_key'] = licence_url + '|Content-Type=&User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3041.0 Safari/537.36&x-custom-data=%s|R{SSM}|' % xcdata_value

    return item
