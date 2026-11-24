# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Jeff2900
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import base64
import re
import json
import uuid

from codequick import Listitem, Resolver, Route, Script
import urlquick

from resources.lib import resolver_proxy, web_utils
from resources.lib.menu_utils import item_post_treatment

URL_ROOT = 'https://novo19.ouest-france.fr'
URL_BASE = 'https://novo19-bff.ouest-france.fr'
URL_BYPATH = URL_BASE + '/api/1/public/frontends/tv/pages/by-path'
REDBEE_BASE_URL = 'https://exposure.api.redbee.live/v2/customer/OuestFrance/businessunit/novoplus'

DEVICEID = str(uuid.UUID(int=uuid.getnode()))
GENERIC_HEADERS = {'User-Agent': web_utils.get_random_ua()}


@Route.register
def list_categories(plugin, item_id, **kwargs):
    """
    Build categories listing
    - Nos documentaires et magazines
    - Nos films
    - ...
    """
    category_root_url = None
    json_resp1 = urlquick.get(URL_BYPATH + '/categories', headers=GENERIC_HEADERS, max_age=-1).json()

    if json_resp1['page'].get('rails'):
        category_root_url = json_resp1['page']['rails'][0].get('src')

    if category_root_url:
        json_resp2 = urlquick.get(URL_BASE + category_root_url, headers=GENERIC_HEADERS, max_age=-1).json()

        for datas in json_resp2.get('tiles') or []:
            category_url = datas.get('href')
            if category_url is None or category_url == '/podcasts':
                continue

            category_image = datas['thumbnail'].get('src')

            json_resp3 = urlquick.get(URL_BYPATH + category_url, headers=GENERIC_HEADERS, max_age=-1).json()
            category_title = json_resp3['page'].get('title')
            category_desc = json_resp3['page']['metadata'].get('description')

            item = Listitem()
            item.label = category_title
            if category_desc:
                item.info['plot'] = category_desc
            item.art['thumb'] = item.art['landscape'] = category_image
            item.set_callback(list_programs, url=category_url)
            item_post_treatment(item)
            yield item

    # Search feature
    item = Listitem.search(search)
    item_post_treatment(item)
    yield item


@Route.register
def search(plugin, search_query, **kwargs):
    if search_query is None or len(search_query) == 0:
        return False

    at_least_one_item = False
    search_url = None
    json_resp1 = urlquick.get(URL_BYPATH + '/recherche', headers=GENERIC_HEADERS, max_age=-1).json()

    if json_resp1.get('page'):
        search_url = json_resp1['page'].get('src')

    if search_url:
        json_resp2 = urlquick.get(URL_BASE + search_url, params={'query': search_query}, headers=GENERIC_HEADERS, max_age=-1).json()

        for datas in json_resp2.get('tiles') or []:
            program_type = datas.get('type')
            program_id = datas.get('id')
            if program_id is None:
                continue
            program_title = datas.get('title')
            program_subtitle = datas.get('subtitle')
            program_desc = datas.get('description')
            thumbnail = datas.get('thumbnail') or {}
            program_image = thumbnail.get('src')
            program_duration = datas.get('duration')
            program_url = datas.get('href')

            if program_subtitle and program_type == 'EPISODE':
                program_title = program_subtitle + ' - ' + program_title

            at_least_one_item = True
            item = Listitem()
            item.label = program_title
            item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = program_image
            if program_desc:
                item.info['plot'] = program_desc
            if program_duration:
                item.info['duration'] = program_duration
            if program_type == 'SERIE':
                item.set_callback(list_seasons, url=program_url)
            elif program_type == 'COLLECTION':
                item.set_callback(list_programs, url=program_url)
            else:
                item.set_callback(get_video_url, video_id=program_id)

            item_post_treatment(item)
            yield item

    if not at_least_one_item:
        plugin.notify(plugin.localize(30718), '')
        yield False


@Route.register
def list_programs(plugin, url, **kwargs):
    """
    Build programs listing
    - Journal de 20H
    - Cash investigation
    """
    if '/api/1/public/frontends' in url:
        json_resp1 = urlquick.get(URL_BASE + url, headers=GENERIC_HEADERS, max_age=-1).json()
        for datas in json_resp1.get('tiles') or []:
            program_type = datas.get('type')
            program_id = datas.get('id')
            if program_id is None:
                continue
            program_title = datas.get('title')
            program_subtitle = datas.get('subtitle')
            program_desc = datas.get('description')
            thumbnail = datas.get('thumbnail') or {}
            program_image = thumbnail.get('src')
            program_duration = datas.get('duration')
            program_url = datas.get('href')
            if program_subtitle and program_type == 'EPISODE':
                program_title = program_subtitle + ' - ' + program_title
            if program_title is None:
                program_title = (program_url or '').rstrip('/').split('/')[-1].title()

            item = Listitem()
            item.label = program_title
            item.art['thumb'] = item.art['landscape'] = program_image
            if program_desc:
                item.info['plot'] = program_desc
            if program_duration:
                item.info['duration'] = program_duration
            if program_type == 'SERIE':
                item.set_callback(list_seasons, url=program_url)
            elif program_type == 'COLLECTION':
                item.set_callback(list_programs, url=program_url)
            else:
                item.set_callback(get_video_url, video_id=program_id)

            item_post_treatment(item)
            yield item
    else:
        json_resp2 = urlquick.get(URL_BYPATH + url, headers=GENERIC_HEADERS, max_age=-1).json()
        json_parse = json_resp2['page']
        if json_parse['type'] == 'DETAILS':
            program_title = json_parse.get('title')
            if json_parse.get('content'):
                playback_infos = json_parse.get('playbackInfos') or []
                if json_parse.get('content') and playback_infos:
                    program_id = playback_infos[0].get('assetId')
                program_desc = json_parse['content'].get('description')
                program_image_bg = json_parse['content']['background'].get('src')
                program_image = json_parse['content']['thumbnail'].get('src')

                item = Listitem()
                item.label = program_title
                if program_desc:
                    item.info['plot'] = program_desc
                item.art['thumb'] = item.art['landscape'] = program_image
                item.art["fanart"] = program_image_bg
                item.set_callback(get_video_url, video_id=program_id)
                item_post_treatment(item)
                yield item

        if json_parse['rails']:
            program_image = None
            program_desc = json_parse['metadata'].get('description')
            if json_parse['metadata'].get('image'):
                program_image = json_parse['metadata'].get('image').get('src')

            for datas in json_parse.get('rails') or {}:
                program_type = datas.get('textLayout')
                if program_type != 'BOTTOM':
                    continue

                program_id = datas.get('id')
                if program_id == 'reco':
                    continue

                program_title = datas.get('title')
                program_url = datas.get('src')
                resp = urlquick.get(URL_BYPATH + program_url, headers=GENERIC_HEADERS, max_age=-1)
                program_tiles = resp.json().get('tiles')
                if len(program_tiles) == 0:
                    continue

                item = Listitem()
                item.label = program_title
                if program_desc:
                    item.info['plot'] = program_desc
                if program_image:
                    item.art['thumb'] = item.art['landscape'] = program_image
                item.set_callback(list_programs, url=program_url)
                item_post_treatment(item)
                yield item


@Route.register
def list_seasons(plugin, url, **kwargs):
    season_image = None
    json_resp1 = urlquick.get(URL_BYPATH + url, headers=GENERIC_HEADERS, max_age=-1).json()

    if json_resp1['page'].get('content'):
        season_image_bg = json_resp1['page']['content']['background'].get('src')
        season_image = json_resp1['page']['content']['thumbnail'].get('src')

    if json_resp1['page'].get('rails'):
        season_desc = json_resp1['page']['metadata'].get('description')
        if season_image is None:
            season_image = json_resp1['page']['metadata']['image'].get('src')

        for datas in json_resp1['page']['rails'] or {}:
            season_type = datas.get('textLayout')
            if season_type != 'BOTTOM':
                continue
            season_id = datas.get('id')
            if season_id == 'reco':
                continue
            season_title = datas.get('title')
            season_url = datas.get('src')

            json_resp2 = urlquick.get(URL_BYPATH + season_url, headers=GENERIC_HEADERS, max_age=-1).json()
            videos_tiles = json_resp2.get('tiles')
            if len(videos_tiles) == 0:
                continue
            if json_resp2.get('more'):
                video_url_all = json_resp2['more'].get('href')
                if video_url_all:
                    json_resp3 = urlquick.get(URL_BYPATH + video_url_all, headers=GENERIC_HEADERS, max_age=-1).json()
                    if json_resp3.get('page'):
                        season_url = json_resp3['page'].get('src')

            item = Listitem()
            item.label = season_title
            if season_desc:
                item.info['plot'] = season_desc
            if season_image:
                item.art['thumb'] = item.art['landscape'] = season_image
            if season_image_bg:
                item.art["fanart"] = season_image_bg
            item.set_callback(list_videos, video_url=season_url)
            item_post_treatment(item)
            yield item


@Route.register
def list_videos(plugin, video_url, **kwargs):
    video_url_all = None
    at_least_one_item = False
    json_resp = urlquick.get(URL_BASE + video_url, headers=GENERIC_HEADERS, max_age=-1).json()

    if json_resp.get('more'):
        video_url_all = URL_BASE + json_resp['more'].get('href')

    for datas in json_resp.get('tiles') or {}:
        videos_id = datas.get('id')
        if videos_id is None:
            continue

        videos_title = datas.get('title')
        videos_subtitle = datas.get('subtitle')
        videos_desc = datas.get('description')
        thumbnail = datas.get('thumbnail') or {}
        videos_image = thumbnail.get('src')
        videos_duration = datas.get('duration')
        if videos_subtitle:
            video_label = videos_subtitle + ' - ' + videos_title
        else:
            video_label = videos_title

        at_least_one_item = True
        item = Listitem()
        item.label = video_label
        if videos_desc:
            item.info['plot'] = videos_desc
        if videos_duration:
            item.info['duration'] = videos_duration
        if videos_image:
            item.art['thumb'] = item.art['landscape'] = videos_image
        item.set_callback(get_video_url,
                          video_id=videos_id)
        item_post_treatment(item)
        yield item

    if video_url_all:
        yield Listitem.next_page(video_url=video_url_all)

    # No item found
    if not at_least_one_item:
        item = Listitem()
        item.label = Script.localize(30896)
        item_post_treatment(item)
        yield item


@Resolver.register
def get_video_url(plugin, video_id, **kwargs):
    return get_video_redbee(plugin, video_id, is_drm=True)


def get_redbee_token():
    json_data = {
        'device': {
            'name': 'Browser',
            'type': 'WEB',
        },
        'deviceId': DEVICEID,
    }
    response = urlquick.post(REDBEE_BASE_URL + '/auth/anonymous', headers=GENERIC_HEADERS, json=json_data, max_age=-1).json()
    if response.get('sessionToken'):
        return True, response.get('sessionToken')
    else:
        return False, None


@Route.register
def get_video_redbee(plugin, video_id, is_drm, **kwargs):
    is_ok, session_token = get_redbee_token()
    if is_ok is False:
        return False

    video_format, forced_drm = get_redbee_format(plugin, video_id, session_token, is_drm)
    if video_format is None:
        return False

    video_url = video_format['mediaLocator']

    if not is_drm and not forced_drm:
        if re.match('.*m3u8.*', video_url) is not None:
            return resolver_proxy.get_stream_with_quality(plugin, video_url=video_url, manifest_type="hls")
        return video_url

    certificate_data = None
    if 'drm' in video_format:
        license_server_url = video_format['drm']['com.widevine.alpha']['licenseServerUrl']
        certificate_url = video_format['drm']['com.widevine.alpha'].get('certificateUrl')
        if len(certificate_url) > 0:
            resp_cert = urlquick.get(certificate_url, headers=GENERIC_HEADERS, max_age=-1).text
            certificate_data = base64.b64encode(resp_cert.encode("utf-8")).decode("utf-8")
    else:
        return resolver_proxy.get_stream_with_quality(plugin, video_url=video_url, manifest_type="mpd")

    # TODO subtitles?
    # subtitles = video_format['sprites'][0]['vtt']

    headers = {
        'User-Agent': web_utils.get_random_ua(),
        'Content-Type': ''
    }

    input_stream_properties = {}
    if certificate_data is not None:
        input_stream_properties = {"server_certificate": certificate_data}

    return resolver_proxy.get_stream_with_quality(plugin, video_url=video_url, manifest_type='mpd', headers=headers,
                                                  license_url=license_server_url,
                                                  input_stream_properties=input_stream_properties)


def get_redbee_format(plugin, media_id, session_token, is_drm):
    url = REDBEE_BASE_URL + '/entitlement/{}/play'.format(media_id)

    headers = {
        'User-Agent': web_utils.get_random_ua(),
        'authorization': 'Bearer {}'.format(session_token)
    }
    response = urlquick.get(url, headers=headers, max_age=-1, raise_for_status=False)
    if response.status_code != 200:
        plugin.notify(plugin.localize(30600), plugin.localize(30716))
        return None, True

    json_paser = json.loads(response.text)
    formats = json_paser['formats']

    if not is_drm:
        for fmt in formats:
            if fmt['format'] == 'HLS' and 'drm' not in fmt:
                return fmt, is_drm

    # all formats have drm, switch to DASH
    for fmt in formats:
        if fmt['format'] == 'DASH':
            return fmt, True

    return None, True


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    return get_video_redbee(plugin, 'novo19_565BFFb', is_drm=True)
