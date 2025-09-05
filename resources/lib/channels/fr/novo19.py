# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Jeff2900
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import base64
import re
import json
import uuid

from codequick import Listitem, Resolver, Route
import urlquick

from resources.lib import resolver_proxy, web_utils
from resources.lib.menu_utils import item_post_treatment


URL_ROOT = 'https://novo19.ouest-france.fr'
URL_CATEGORIES = URL_ROOT + '/categories'
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
    response = urlquick.get(URL_CATEGORIES, headers=GENERIC_HEADERS, max_age=-1)
    root = response.parse()

    for category_datas in root.iterfind(".//div[@class='mb-3 flex justify-between align-middle']"):
        if category_datas.find(".//a") is None:
            continue
        category_label = category_datas.find(".//h3").text
        category_url = URL_ROOT + category_datas.find(".//a").get('href')

        item = Listitem()
        item.label = category_label
        item.set_callback(list_programs,
                          item_id=item_id,
                          category_url=category_url)
        item_post_treatment(item)
        yield item


@Route.register
def list_programs(plugin, item_id, category_url, **kwargs):
    """
    Build programs listing
    - Journal de 20H
    - Cash investigation
    """
    response = urlquick.get(category_url, headers=GENERIC_HEADERS, max_age=-1)
    root = response.parse()

    for program_datas in root.iterfind(".//a[@class='tile']"):
        program_title = program_datas.find(".//p").text
        program_label = program_datas.find(".//h3").text
        program_url = URL_ROOT + program_datas.get('href')
        program_image = URL_ROOT + program_datas.find(".//img").get('src')

        item = Listitem()
        item.label = program_title + ' - ' + program_label
        item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = program_image
        item.set_callback(list_videos,
                          item_id=item_id,
                          video_url=program_url)
        item_post_treatment(item)
        yield item


@Route.register
def list_videos(plugin, item_id, video_url, **kwargs):
    """
    Build programs listing
    - Journal de 20H
    - Cash investigation
    """
    response = urlquick.get(video_url, headers=GENERIC_HEADERS, max_age=-1)
    root = response.parse()
    at_least_one_item = False

    for program_datas in root.iterfind(".//a[@class='tile']"):
        program_title = program_datas.find(".//p").text
        program_label = program_datas.find(".//h3").text
        program_url = program_datas.get('href')
        program_image = URL_ROOT + program_datas.find(".//img").get('src')
        program_url_split = program_url.split('/')

        if program_url_split[1] == 'details':
            continue

        at_least_one_item = True
        item = Listitem()
        item.label = program_title + ' - ' + program_label
        item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = program_image
        item.set_callback(get_video_url,
                          video_id=program_url_split[2])
        item_post_treatment(item)
        yield item

    if at_least_one_item is False:
        data = response.parse("script", attrs={"id": "__NEXT_DATA__"})
        json_parser = json.loads(data.text)
        program_id = json_parser['props']['pageProps']['serverData']['page']['content']['id']
        program_title = json_parser['props']['pageProps']['serverData']['page']['content']['title']
        program_desc = json_parser['props']['pageProps']['serverData']['page']['content']['description']
        program_image = json_parser['props']['pageProps']['serverData']['page']['content']['background']['src']
        program_date = json_parser['props']['pageProps']['serverData']['page']['content']['releaseDate']
        program_duration = json_parser['props']['pageProps']['serverData']['page']['content']['duration']

        item = Listitem()
        item.label = program_title
        item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = program_image
        item.info['plot'] = program_desc
        item.info['year'] = program_date
        item.info['duration'] = program_duration
        item.set_callback(get_video_url,
                          video_id=program_id)
        item_post_treatment(item)
        yield item


@Resolver.register
def get_video_url(plugin, video_id):
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
def get_video_redbee(plugin, video_id, is_drm):
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
