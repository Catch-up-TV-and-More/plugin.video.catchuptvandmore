# -*- coding: utf-8 -*-
# Copyright: (c) 2026
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import base64
import html
import json
import re
import requests
import urlquick
from codequick import Listitem, Resolver
from datetime import datetime, timedelta, timezone
from kodi_six import xbmcgui
from urllib.parse import urlencode

from resources.lib.kodi_utils import (INPUTSTREAM_PROP, get_selected_item_art,
                                      get_selected_item_info,
                                      get_selected_item_label)

from resources.lib import web_utils

URL_ROOT = 'https://www.rte.ie'
WEB_CONFIG_JSON = URL_ROOT + "/wordpress/wp-content/uploads/standard/web/config.json"
URL_LICENSE = "https://widevine.entitlement.eu.theplatform.com/wv/web/ModularDrm"
LICENSE_HEADERS = "Content-Type=application/json"

CONFIG_JSON = requests.get(WEB_CONFIG_JSON).json()
ACCOUNT_ID = CONFIG_JSON["mpx_config"]["account_id"]

FEED_URLS = {
    feed["type"]: feed["endpoint"]
    for feed in CONFIG_JSON["mpx_config"]["feeds"]
}

def get_feed_url(feed_type):
    try:
        return FEED_URLS[feed_type]
    except KeyError:
        raise ValueError(f"No feed found for type '{feed_type}'")
def get_token():
    return requests.get(CONFIG_JSON["anonymous_autologin_url"]).json()["mpx_token"]

def get_manifest_and_pid(plugin, media_url, token):
    headers = {
        'authorization': 'Basic ' + base64.b64encode((ACCOUNT_ID + ':' + token).encode()).decode(),
    }

    params = {
        'format': 'SMIL',
        'embedded': 'true',
        'tracking': 'true',
        'formats': 'mpeg-dash',
        'appVers': 'P_Web_3 3.164.2',
        'policy': '123034966',
        'iu': '/3014/RTE_Player_Live/Desktop_Web/NotRegistered',
    }

    response = requests.get(media_url, params=params, headers=headers)
    media_html = response.text

    if "GeoLocationBlocked" in media_html:
        plugin.notify("ERROR", plugin.localize(30713))
        return None, None

    manifest_match = re.search(r'src="(https?://[^/"]+[^"]*?\.mpd\?[^"]+)"', media_html)
    pid_match = re.search(r'(?<=\bpid=)[^|"]+', media_html)

    if manifest_match and pid_match:
        manifest = html.unescape(manifest_match.group(1))
        pid = pid_match.group(0)
        return manifest, pid
    return None, None


def build_rte_list_item(plugin, media_url) -> Listitem:
    token = get_token()

    manifest, pid = get_manifest_and_pid(plugin, media_url, token)

    if manifest is None or pid is None:
        return None

    return get_the_platform_list_item(manifest, pid, token)


def get_the_platform_list_item(manifest, pid, token) -> Listitem:
    params = {
        "token": token,
        "account": ACCOUNT_ID,
        "form": "json",
        "schema": "1.0",
    }

    license_url = f"{URL_LICENSE}?{urlencode(params)}"

    payload = json.dumps({
        "getWidevineLicense": {
            "releasePid": pid,
            "widevineChallenge": "b{SSM}"
        }
    })

    item = Listitem()
    item.path = manifest
    item.property[INPUTSTREAM_PROP] = 'inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property['inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property['inputstream.adaptive.license_key'] = '%s|%s|%s|JBlicense' % (license_url, LICENSE_HEADERS, payload)
    return item


def get_live_media_url(guid):
    start_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    end_ms = start_ms + int(timedelta(days=1).total_seconds() * 1000)

    params = {
        "byListingTime": f"{start_ms}~{end_ms}",
        "byCallSign": guid,
        "maxListings": 30,
    }

    schedules_json = requests.get(get_feed_url('allStationsSchedule'), params).json()
    entry = next(
        (r for r in schedules_json.get('entries', []) if r.get('guid') == guid),
        None
    )
    media_pid = entry['plchannelschedule$listings'][0]['rtelisting$mediaPid']
    media_url = get_feed_url('LinearBaseUrl') + media_pid
    return media_url


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    media_url = get_live_media_url(item_id)

    item = build_rte_list_item(plugin, media_url)
    if item:
        item.label = get_selected_item_label()
        item.art.update(get_selected_item_art())
        item.info.update(get_selected_item_info())
        return item
    return None
