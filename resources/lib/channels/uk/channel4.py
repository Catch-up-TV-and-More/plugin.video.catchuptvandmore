# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Joaopa
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More
# Partially based on Diazole's work (https://github.com/Diazole/c4-dl)

from __future__ import unicode_literals

import base64
import re
import json

from codequick import Listitem, Resolver, Route
import urlquick

from resources.lib.kodi_utils import get_kodi_version, get_selected_item_art, get_selected_item_label, get_selected_item_info, INPUTSTREAM_PROP
from resources.lib.menu_utils import item_post_treatment

from resources.lib import resolver_proxy, web_utils

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

URL_ROOT = 'https://www.channel4.com'
URL_CATEGORIES = URL_ROOT + '/api/homepage'
URL_VOD = URL_ROOT + '/vod/stream/'
URL_LICENSE = 'https://c4.eme.lp.aws.redbeemedia.com/wvlicenceproxy-service/widevine/acquire'

URL_LIVE = URL_ROOT + '/simulcast/channels/%s'

BASIC_HEADERS = {'User-Agent': web_utils.get_random_ua()}
LICENSE_HEADERS = "User-Agent=%s&Content-Type=application/json&Referer=%s" % (web_utils.get_random_ua(), URL_ROOT)


@Route.register
def list_categories(plugin, **kwargs):
    resp = urlquick.get(URL_CATEGORIES, headers=BASIC_HEADERS, max_age=-1)
    json_parser = json.loads(resp.text)

    for b in json_parser['slices']:
        for key, value in b.items():
            if key == 'title' and value == 'Categories':
                for d in b['sliceItems']:
                    url_item = d['url']
                    item = Listitem()
                    item.label = url_item.replace('/', ' ').split()[-1]
                    item.art["thumb"] = item.art["landscape"] = d['image']['href']
                    item.set_callback(list_programs, url=url_item.replace('http', 'https'))
                    item_post_treatment(item)
                    yield item


@Route.register
def list_programs(plugin, url, **kwargs):
    """
    Build programs listing
    """
    programs_category = urlquick.get(url, headers=BASIC_HEADERS, max_age=-1).parse()
    programs_number = programs_category.findall(".//div[@class='all4-text all4-typography-body discovery-header__text  secondary']")[0].text.replace('(', ' ').split()[0]

    program_counter = 0

    while program_counter <= int(programs_number):
        for program in programs_category.iterfind(".//a[@class='all4-slice-item']"):
            program_counter += 1
            item = Listitem()
            item.label = program.find('.//h3').text
            item.art["thumb"] = item.art["landscape"] = program.find('.//img').get('src')
            item.set_callback(list_seasons, url=program.get('href'))
            item.info['plot'] = program.get('aria-label')
            item_post_treatment(item)
            yield item
        if program_counter % 20 == 0:
            programs_category = urlquick.get(url + '?offset={}'.format(program_counter), headers=BASIC_HEADERS, max_age=-1).parse()


@Route.register
def list_seasons(plugin, url, **kwargs):
    html_text = urlquick.get(url, headers=BASIC_HEADERS, max_age=-1).parse()

    for script in html_text.iterfind('.//script'):
        script_text = script.text
        if script_text is not None and script_text.split()[0] == 'window.__PARAMS__':
            datas = json.loads(re.sub(r'^.*?{', '{', script_text).replace("undefined", "{}"))
            series = datas['initialData']['brand']['series']
            for season in series:
                series_number = season['seriesNumber']
                item = Listitem()
                item.label = season['title']
                item.art["thumb"] = item.art["landscape"] = datas['initialData']['brand']['images']['image16x9']['src']
                item.set_callback(get_episodes_list, series, series_number, datas)
                item.info['plot'] = season['summary']
                item_post_treatment(item)
                yield item


@Route.register
def get_episodes_list(plugin, series, series_number, datas, **kwargs):
    for episode in datas['initialData']['brand']['episodes']:
        if episode['seriesNumber'] == series_number and episode.get('assetId'):
            item = Listitem()
            item.label = episode['title'].replace(series[len(series) - series_number]['title'], '')
            item.label = item.label + " ({})".format(episode['originalTitle'])
            item.art['thumb'] = item.art['landscape'] = episode['image']['src']
            item.set_callback(get_video, programmeId=episode['programmeId'], assetId=episode['assetId'])
            item.info['plot'] = episode['summary']
            item_post_treatment(item)
            yield item


@Resolver.register
def get_video(plugin, programmeId, assetId, **kwargs):
    url_video_json = URL_VOD + '{}'.format(programmeId)
    resp = urlquick.get(url_video_json, max_age=-1)

    json_video = json.loads(resp.text)
    for field in json_video['videoProfiles']:
        if field['name'] == 'dashwv-dyn-stream-1':
            token = field['streams'][0]['token']
            url = field['streams'][0]['uri']
            break

    cipher = AES.new(bytes('n9cLieYkqwzNCqvi', 'UTF-8'), AES.MODE_CBC, bytes('odzcU3WdUiXLucVd', 'UTF-8'))
    decoded_token = unpad(cipher.decrypt(base64.b64decode(token)), 16, style='pkcs7').decode('UTF-8').split('|')[1]

    payload = json.dumps({
        "request_id": assetId,
        "token": decoded_token,
        "video": {
            "type": "ondemand",
            "url": url
        },
        "message": "b{SSM}"
    })

    item = Listitem()
    item.path = url
    item.label = get_selected_item_label()
    item.art.update(get_selected_item_art())
    item.info.update(get_selected_item_info())
    item.property[INPUTSTREAM_PROP] = 'inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property['inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property['inputstream.adaptive.license_key'] = '%s|%s|%s|JBlicense' % (URL_LICENSE, LICENSE_HEADERS, payload)

    return item


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    url_video_json = URL_LIVE % item_id
    resp = urlquick.get(url_video_json, max_age=-1)

    json_video = json.loads(resp.text)
    for field in json_video['channelInfo']['videoProfiles']:
        if field['name'] == 'dashwv-live-stream-iso-dash-sp-tl':
            token = field['streams'][0]['token']
            url = field['streams'][0]['uri']
            break

    cipher = AES.new(bytes('n9cLieYkqwzNCqvi', 'UTF-8'), AES.MODE_CBC, bytes('odzcU3WdUiXLucVd', 'UTF-8'))
    full_decoded_token = unpad(cipher.decrypt(base64.b64decode(token)), 16, style='pkcs7').decode('UTF-8')
    decoded_token = re.compile(r'\&t\=(.*?)$').findall(full_decoded_token)[0]

    payload = json.dumps({
        "token": decoded_token,
        "video": {
            "type": "simulcast",
            "url": url
        },
        "message": "b{SSM}"
    })

    item = Listitem()
    item.path = url
    item.label = get_selected_item_label()
    item.art.update(get_selected_item_art())
    item.info.update(get_selected_item_info())
    item.property[INPUTSTREAM_PROP] = 'inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property['inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property['inputstream.adaptive.license_key'] = '%s|%s|%s|JBlicense' % (URL_LICENSE, LICENSE_HEADERS, payload)

    return item
