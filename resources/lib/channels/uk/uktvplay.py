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

# The unicode_literals import only has
# an effect on Python 2.
# It makes string literals as unicode like in Python 3
from __future__ import unicode_literals

from codequick import Route, Resolver, Listitem, utils, Script

from resources.lib.labels import LABELS
from resources.lib import web_utils
from resources.lib import resolver_proxy
import resources.lib.cq_utils as cqu


import inputstreamhelper
import json
import re
import requests
import urlquick
import xbmc
import xbmcgui


# TO DO
# Replay protected by SAMPLE-AES (keep code - desactivate channel for the moment)


URL_ROOT = 'https://uktvplay.uktv.co.uk'

URL_BRIGHTCOVE_DATAS = 'https://s3-eu-west-1.amazonaws.com/uktv-static/prod/play/%s.js'
# JS_id
# https://s3-eu-west-1.amazonaws.com/uktv-static/prod/play/35639012dd82fd7809e9.js

URL_BRIGHTCOVE_POLICY_KEY = 'http://players.brightcove.net/%s/%s_default/index.min.js'
# AccountId, PlayerId

URL_BRIGHTCOVE_VIDEO_JSON = 'https://edge.api.brightcove.com/'\
                            'playback/v1/accounts/%s/videos/%s'
# AccountId, VideoId

URL_API = 'https://vschedules.uktv.co.uk'

LETTER_LIST = ["0-9","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

URL_PROGRAMS = URL_API + '/vod/brand_list/?starts_with=%s&letter_name=%s&is_watchable=True'
# Letter

URL_INFO_PROGRAM = URL_API + '/vod/brand/?slug=%s'
# Program_slug

URL_VIDEOS = URL_API + '/vod/series/?id=%s'
# Serie_ID


def replay_entry(plugin, item_id):
    """
    First executed function after replay_bridge
    """
    return list_letters(plugin, item_id)


@Route.register
def list_letters(plugin, item_id):
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
            letter_value=letter_value)
        yield item


@Route.register
def list_programs(plugin, item_id, letter_value):

    resp = urlquick.get(URL_PROGRAMS % (letter_value.replace('0-9', '0'), letter_value))
    json_parser = json.loads(resp.text)

    for program_datas in json_parser:
        program_title = program_datas['name']
        program_image = ''
        if 'image' in program_datas:
            program_image = program_datas['image']
        program_slug = program_datas['slug']

        item = Listitem()
        item.label = program_title
        item.art['thumb'] = program_image
        item.set_callback(
            list_seasons,
            item_id=item_id,
            program_slug=program_slug)
        yield item


@Route.register
def list_seasons(plugin, item_id, program_slug):

    resp = urlquick.get(URL_INFO_PROGRAM % program_slug)
    json_parser = json.loads(resp.text)

    for season_datas in json_parser["series"]:
        season_title = 'Season - ' + season_datas['number']
        serie_id = season_datas["id"]

        item = Listitem()
        item.label = season_title
        item.set_callback(
            list_videos,
            item_id=item_id,
            serie_id=serie_id)
        yield item


@Route.register
def list_videos(plugin, item_id, serie_id):

    resp = urlquick.get(URL_VIDEOS % serie_id)
    json_parser = json.loads(resp.text)

    for video_datas in json_parser["episodes"]:
        video_title = video_datas["brand_name"] + \
            ' - ' ' S%sE%s' % (video_datas["series_number"], str(video_datas["episode_number"])) + ' - ' + video_datas["name"]
        video_image = video_datas["image"]
        video_plot = video_datas["synopsis"]
        video_duration = video_datas["duration"] * 60
        video_id = video_datas["video_id"]

        item = Listitem()
        item.label = video_title
        item.art['thumb'] = video_image
        item.info['plot'] = video_plot
        item.info['duration'] = video_duration
        item.set_callback(
            get_video_url,
            item_id=item_id,
            data_video_id=video_id,
            item_dict=cqu.item2dict(item))
        yield item


# BRIGHTCOVE Part
def get_brightcove_policy_key(data_account, data_player):
    """Get policy key"""
    file_js = urlquick.get(
        URL_BRIGHTCOVE_POLICY_KEY % (data_account, data_player))
    return re.compile('policyKey:"(.+?)"').findall(file_js.text)[0]


@Resolver.register
def get_video_url(plugin, item_id, data_video_id, item_dict):

    xbmc_version = int(xbmc.getInfoLabel("System.BuildVersion").split('-')[0].split('.')[0])

    if xbmc_version < 18:
        xbmcgui.Dialog().ok(
            'Info',
            plugin.localize(30602))
        return False

    is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
    if not is_helper.check_inputstream():
        return False

    # create session request
    session_requests = requests.session()

    # Get data_account / data_player
    resp = session_requests.get(URL_ROOT)
    js_id_all = re.compile(
        r'uktv\-static\/prod\/play\/(.*?)\.js').findall(resp.text)
    for js_id in js_id_all:
        resp2 = session_requests.get(URL_BRIGHTCOVE_DATAS % js_id)
        if len(re.compile(r'VUE_APP_BRIGHTCOVE_ACCOUNT\:\"(.*?)\"').findall(resp2.text)) > 0:
            data_account = re.compile(
                r'VUE_APP_BRIGHTCOVE_ACCOUNT\:\"(.*?)\"').findall(resp2.text)[0]
            data_player = re.compile(
                r'VUE_APP_BRIGHTCOVE_PLAYER\:\"(.*?)\"').findall(resp2.text)[0]
            break

    # Method to get JSON from 'edge.api.brightcove.com'
    resp3 = session_requests.get(
        URL_BRIGHTCOVE_VIDEO_JSON % (data_account, data_video_id),
        headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
            'Accept': 'application/json;pk=%s' % (get_brightcove_policy_key(data_account, data_player))})

    json_parser = json.loads(resp3.text)

    video_url = ''
    licence_key = ''
    if 'sources' in json_parser:
        for url in json_parser["sources"]:
            if 'src' in url:
                if 'com.widevine.alpha' in url["key_systems"]:
                    video_url = url["src"]
                    licence_key = url["key_systems"]['com.widevine.alpha']['license_url']

    item = Listitem()
    item.path = video_url
    item.label = item_dict['label']
    item.info.update(item_dict['info'])
    item.art.update(item_dict['art'])
    item.property['inputstreamaddon'] = 'inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property['inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property['inputstream.adaptive.license_key'] = licence_key + '|Content-Type=&User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3041.0 Safari/537.36&Host=manifest.prod.boltdns.net|R{SSM}|'

    return item
