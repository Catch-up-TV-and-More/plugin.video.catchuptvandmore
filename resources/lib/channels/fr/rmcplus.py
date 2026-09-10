# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Jeff2900
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import json
import re

from codequick import Listitem, Resolver, Route, Script
import urlquick

from kodi_six import xbmcgui, xbmcplugin
from resources.lib import resolver_proxy, web_utils
from resources.lib.menu_utils import item_post_treatment

URL_ROOT = 'https://bff.rmcplus.fr/v1'
URL_ROOT_PARAMS = '&model=androidtv-ott'
URL_SIGNIN = 'https://connect.rmcbfm.com/api/sign-in?model=androidtv-ott'
URL_CLIENTID = 'https://www.rmcplus.fr/_next/static/chunks/0lucft_--p463.js'
URL_LICENCE_KEY = 'https://lic.drmtoday.com/license-proxy-widevine/cenc/|Content-Type=&User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3041.0 Safari/537.36&Host=lic.drmtoday.com&x-dt-auth-token=%s|R{SSM}|JBlicense'

# GENERIC_HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36'}
GENERIC_HEADERS = {'User-Agent': web_utils.get_random_windows_ua(), }

LIVE_CHANNEL = {
    "BFM TV": "bfmtv",
    "RMC STORY": "rmc_story",
    "RMC Découverte": "rmc_decouverte",
    "RMC Life": "rmc_life",
}


def get_login_token(plugin):
    if plugin.setting.get_string('rmcplus.login') == '' or plugin.setting.get_string('rmcplus.password') == '':
        xbmcgui.Dialog().ok('Info', plugin.localize(30604) % ('RMC+', 'https://www.rmcplus.fr'))
        return False

    user = plugin.setting.get_string('rmcplus.login')
    password = plugin.setting.get_string('rmcplus.password')

    # Get ClientId
    headers = {
        'User-Agent': web_utils.get_random_windows_ua(),
        'Accept': '*/*',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://www.rmcplus.fr/',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    resp = urlquick.get(URL_CLIENTID, headers=headers, max_age=-1)
    PATTERN_CLIENTID = re.compile(r"\"getEffectiveAuthenticationClientId\",0,\(\)=>\"([^\"]*)")
    clientid = PATTERN_CLIENTID.findall(resp.text)

    # Get login Token
    json_body = {
        "email": user,
        "password": password,
        "clientId": clientid[0]
    }
    headers = {
        'User-Agent': web_utils.get_random_windows_ua(),
        'Accept-Encoding': 'gzip',
        'Connection': 'Keep-Alive',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'connect.rmcbfm.com',
    }

    resp = urlquick.post(URL_SIGNIN, headers=headers, json=json_body, max_age=-1, raise_for_status=False)
    if resp.status_code != 200:
        plugin.notify('ERROR', 'RMC+ : ' + plugin.localize(30711))
        return False

    idtoken = resp.json()['AuthenticationResult'].get('IdToken')
    return idtoken


@Route.register
def rmcplus_root(plugin, **kwargs):
    # Channels
    item = Listitem()
    item.label = Script.localize(30006)
    item.set_callback(channels)
    item_post_treatment(item)
    yield item

    # Categories
    item = Listitem()
    item.label = Script.localize(30725)
    item.set_callback(categories)
    item_post_treatment(item)
    yield item

    # Search feature
    item = Listitem.search(search)
    item_post_treatment(item)
    yield item


@Route.register
def channels(plugin, **kwargs):
    """
    List all rmc+ channels
    """
    # (item_id, label, thumb, fanart)
    params = {
        'page_type': 'default',
        'page_id': 'categories',
        'model': 'androidtv-ott',
    }
    resp = urlquick.get(URL_ROOT + '/page', params=params, headers=GENERIC_HEADERS, max_age=-1)

    for datas in resp.json().get('sections'):
        type_tuile = datas.get('type_tuile')
        titre = datas.get('titre')
        if type_tuile == "categorie" and titre.startswith("Nos"):
            items = datas.get('items')
            if items:
                for item in items:
                    if 'background_image' in item:
                        channel_image = item['background_image'].get('url')
                        channel_title = item['background_image'].get('alt')
                        if len(channel_title) == 0:
                            channel_title = item.get('id')
                    if 'call_to_actions' in item:
                        channel_url = item['call_to_actions'][0].get('endpoint')

                    if channel_url is None:
                        continue
                    if 'http' not in channel_url:
                        channel_url = URL_ROOT + channel_url + URL_ROOT_PARAMS

                    item = Listitem()
                    item.label = channel_title
                    item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = channel_image
                    item.set_callback(list_programs,
                                      category_url=channel_url)
                    item_post_treatment(item)
                    yield item


@Route.register
def categories(plugin, **kwargs):
    """
    Build categories listing
    - Nos documentaires et magazines
    - Nos films
    - ...
    """
    params = {
        'page_type': 'default',
        'page_id': 'categories',
        'model': 'androidtv-ott',
    }
    resp = urlquick.get(URL_ROOT + '/page', params=params, headers=GENERIC_HEADERS, max_age=-1)

    for datas in resp.json().get('sections'):
        type_tuile = datas.get('type_tuile')
        titre = datas.get('titre')
        if type_tuile == "categorie" and titre.startswith("Cat"):
            items = datas.get('items')
            if items:
                for item in items:
                    if 'background_image' in item:
                        category_image = item['background_image'].get('url')
                        category_title = item['background_image'].get('alt')
                        if len(category_title) == 0:
                            category_title = item.get('id')
                    if 'call_to_actions' in item:
                        category_url = item['call_to_actions'][0].get('endpoint')

                    if category_url is None:
                        continue
                    if 'http' not in category_url:
                        category_url = URL_ROOT + category_url + URL_ROOT_PARAMS

                    item = Listitem()
                    item.label = category_title
                    item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = category_image
                    item.set_callback(list_programs,
                                      category_url=category_url)
                    item_post_treatment(item)
                    yield item


@Route.register
def search(plugin, search_query, **kwargs):
    if search_query is None or len(search_query) == 0:
        return False

    params = {
        'page_id': 'recherche',
        'page_type': 'recherche',
        'query': search_query,
        'model': 'androidtv-ott',
    }
    resp = urlquick.get(URL_ROOT + '/recherche', params=params, headers=GENERIC_HEADERS, max_age=-1)

    at_least_one_item = False
    for datas in resp.json().get('sections'):
        datas_titre = datas.get('titre')
        if datas_titre == "Programmes":
            items = datas.get('items')
            if items:
                for array in items:
                    if 'background_image' in array:
                        search_image = array['background_image'].get('url')
                        search_title = array['background_image'].get('alt')
                        if len(search_title) == 0:
                            search_title = array.get('id')
                    if 'call_to_actions' in array:
                        search_url = array['call_to_actions'][0].get('endpoint')
                    if search_url is None:
                        continue
                    if 'http' not in search_url:
                        search_url = URL_ROOT + search_url + URL_ROOT_PARAMS

                    at_least_one_item = True
                    item = Listitem()
                    item.label = search_title
                    item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = search_image
                    item.set_callback(list_videos,
                                      video_url=search_url)
                    item_post_treatment(item)
                yield item

    if not at_least_one_item:
        plugin.notify(plugin.localize(30718), '')
        yield False


@Route.register(autosort=False)
def list_programs(plugin, category_url, **kwargs):
    """
    Build programs listing
    - Journal de 20H
    - Cash investigation
    """
    resp = urlquick.get(category_url, headers=GENERIC_HEADERS, max_age=-1)

    for datas in resp.json().get('sections'):
        items = datas.get('items')
        if items:
            for item in items:
                if 'background_image' in item:
                    program_image = item['background_image'].get('url')
                    program_title = item['background_image'].get('alt')
                    if len(program_title) == 0:
                        program_title = item.get('titre')
                if 'call_to_actions' in item:
                    program_url = item['call_to_actions'][0].get('endpoint')
                if program_url is None:
                    continue
                if 'http' not in program_url:
                    program_url = URL_ROOT + program_url + URL_ROOT_PARAMS

                item = Listitem()
                item.label = program_title
                item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = program_image
                if 'page_type=player' in program_url:
                    item.set_callback(get_video_url,
                                      video_url=program_url)
                else:
                    item.set_callback(list_videos,
                                      video_url=program_url)
                item_post_treatment(item)
                yield item


@Route.register(autosort=False)
def list_videos(plugin, video_url, **kwargs):
    at_least_one_item = False
    resp = urlquick.get(video_url, headers=GENERIC_HEADERS, max_age=-1)

    video_titre = resp.json().get('titre')
    for datas in resp.json().get('sections'):
        datas_type = datas.get('type')
        datas_tuile = datas.get('type_tuile')

        if datas_tuile == "episode" or datas_type == "mosaique":
            items = datas.get('items')
            if items:
                for array in items:
                    at_least_one_item = True
                    video_title = video_desc = video_image = None
                    if 'background_image' in array:
                        video_image = array['background_image'].get('url')
                        video_subtitle = array['background_image'].get('alt')
                        if len(video_subtitle) == 0:
                            video_subtitle = array.get('id')
                    if 'description' in array:
                        video_desc = array.get('description')
                    if 'call_to_actions' in array:
                        video_url = array['call_to_actions'][0].get('endpoint')
                    if video_url is None:
                        continue
                    if 'http' not in video_url:
                        video_url = URL_ROOT + video_url + URL_ROOT_PARAMS

                    if 'etiquette' in array:
                        video_duree = array['etiquette'].get('duree')
                        Hrs_h = Hrs_m = duration = None
                        if video_duree:
                            if 'h' in video_duree:
                                Hrs_h = re.compile(r'(\d+)h').findall(video_duree)
                            if 'm' in video_duree:
                                Hrs_m = re.compile(r'(\d+)m').findall(video_duree)
                            if Hrs_h:
                                if Hrs_m:
                                    duration = int(Hrs_m[0]) + int(60) * int(Hrs_h[0])
                                else:
                                    duration = int(60) * int(Hrs_h[0])
                            elif Hrs_m:
                                duration = int(Hrs_m[0])
                            else:
                                duration = None

                        video_episode = array['etiquette'].get('saison_episode')
                        if video_episode:
                            video_title = video_titre + ' - ' + video_episode + ' - ' + video_subtitle
                        else:
                            video_title = video_titre + ' - ' + video_subtitle

                    item = Listitem()
                    item.label = video_title
                    item.info['plot'] = video_desc
                    item.info['duration'] = duration
                    item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = video_image
                    if 'page_type=player' in video_url:
                        item.set_callback(get_video_url,
                                          video_url=video_url)
                    else:
                        item.set_callback(list_videos,
                                          video_url=video_url)
                    item_post_treatment(item)
                    yield item

    if not at_least_one_item:
        for datas in resp.json().get('sections'):
            datas_type = datas.get('type')
            datas_tuile = datas.get('type_tuile')

            if datas_type == 'herobannerFIP':
                array = datas.get('item')
                if array:
                    video_title = None
                    if 'background_image' in array:
                        video_image = array['background_image'].get('url')
                        video_subtitle = array['background_image'].get('alt')
                        if len(video_subtitle) == 0:
                            video_subtitle = array.get('id')
                            video_title = video_titre + ' - ' + video_subtitle
                        else:
                            video_title = video_titre
                    if 'description' in array:
                        video_desc = array.get('description')
                    if 'call_to_actions' in array:
                        video_url = array['call_to_actions'][0].get('endpoint')
                    if video_url is None or video_title is None:
                        continue
                    if 'http' not in video_url:
                        video_url = URL_ROOT + video_url + URL_ROOT_PARAMS
                    if 'etiquette' in array:
                        video_duree = array['etiquette'].get('duree')
                        Hrs_h = Hrs_m = duration = None
                        if video_duree:
                            if 'h' in video_duree:
                                Hrs_h = re.compile(r'(\d+)h').findall(video_duree)
                            if 'm' in video_duree:
                                Hrs_m = re.compile(r'(\d+)m').findall(video_duree)
                            if Hrs_h:
                                if Hrs_m:
                                    duration = int(Hrs_m[0]) + int(60) * int(Hrs_h[0])
                                else:
                                    duration = int(60) * int(Hrs_h[0])
                            elif Hrs_m:
                                duration = int(Hrs_m[0])
                            else:
                                duration = None

                        video_episode = array['etiquette'].get('saison_episode')
                        if video_episode:
                            video_title = video_titre + ' - ' + video_episode + ' - ' + video_subtitle

                    item = Listitem()
                    item.label = video_title
                    item.info['plot'] = video_desc
                    item.info['duration'] = duration
                    item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = video_image
                    if 'page_type=player' in video_url:
                        item.set_callback(get_video_url,
                                          video_url=video_url)
                    else:
                        item.set_callback(list_videos,
                                          video_url=video_url)
                    item_post_treatment(item)
                    yield item


@Resolver.register
def get_video_url(plugin, video_url, **kwargs):
    token = get_login_token(plugin)
    if not token:
        return False

    headers = {
        'User-Agent': web_utils.get_random_windows_ua(),
        'accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'Authorization': 'Bearer ' + token,
    }
    resp = urlquick.get(video_url, headers=headers, max_age=-1, raise_for_status=False)
    if resp.status_code != 200:
        return False

    final_video_url = final_video_format = license_url = None
    for datas in resp.json().get('sections'):
        if datas.get('video'):
            final_video_url = datas['video'].get('url')
            final_video_format = datas['video'].get('format')
            if final_video_format != 'hls':
                final_video_format = 'mpd'
            isdrm = datas['video'].get('drm')
            if isdrm:
                play_token = datas['video'].get('drm').get('play_token')
                license_url = URL_LICENCE_KEY % play_token

    if final_video_url:
        return resolver_proxy.get_stream_with_quality(
            plugin, video_url=final_video_url, manifest_type=final_video_format,
            license_url=license_url)


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    token = get_login_token(plugin)
    if not token:
        return False

    params = {
        'page_type': 'player',
        'page_id': LIVE_CHANNEL[item_id],
        'model': 'androidtv-ott',
    }
    headers = {
        'User-Agent': web_utils.get_random_windows_ua(),
        'accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'Authorization': 'Bearer ' + token,
    }
    resp = urlquick.get(URL_ROOT + '/page', params=params, headers=headers, max_age=-1, raise_for_status=False)
    if resp.status_code != 200:
        return False

    final_video_url = final_video_format = license_url = None
    for datas in resp.json().get('sections'):
        live_id = datas.get('id')
        if live_id == LIVE_CHANNEL[item_id]:
            if datas.get('video'):
                final_video_url = datas['video'].get('url')
                final_video_format = datas['video'].get('format')
                if final_video_format != 'hls':
                    final_video_format = 'mpd'
                isdrm = datas['video'].get('drm')
                if isdrm:
                    play_token = datas['video'].get('drm').get('play_token')
                    license_url = URL_LICENCE_KEY % play_token

    if final_video_url:
        return resolver_proxy.get_stream_with_quality(
            plugin, video_url=final_video_url, manifest_type=final_video_format,
            license_url=license_url)
