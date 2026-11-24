# -*- coding: utf-8 -*-
# Copyright: (c) 2018, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import json
import urlquick

from codequick import Listitem, Resolver, Route, Script
from resources.lib import resolver_proxy, web_utils

from resources.lib.menu_utils import item_post_treatment

# Live
LIVE_MAIN_URL = 'http://tvpstream.vod.tvp.pl/'

URL_STREAMS = 'https://api.tvp.pl/tokenizer/token/{live_id}'

# map from TVP 3 region name to kodi catchuptvandmore item_id
LIVE_TVP3_REGIONS = {
    "Białystok": "tvp3-bialystok",
    "Bydgoszcz": "tvp3-bydgoszcz",
    "Gdańsk": "tvp3-gdansk",
    "Gorzów Wielkopolski": "tvp3-gorzow-wielkopolski",
    "Katowice": "tvp3-katowice",
    "Kielce": "tvp3-kielce",
    "Kraków": "tvp3-krakow",
    "Lublin": "tvp3-lublin",
    "Łódź": "tvp3-lodz",
    "Olsztyn": "tvp3-olsztyn",
    "Opole": "tvp3-opole",
    "Poznań": "tvp3-poznan",
    "Rzeszów": "tvp3-rzeszow",
    "Szczecin": "tvp3-szczecin",
    "Warszawa": "tvp3-warszawa",
    "Wrocław": "tvp3-wroclaw"
}

# from kodi catchuptvandmore item_id to tvp channel id
CHANNEL_ID_MAP = {
    'tvpinfo': 1455,
    'tvppolonia': 1773,
    'tvpworld': 51656487,
    'tvp1': 1729,
    'tvp2': 1751,
    'tvp3-bialystok': 745680,
    'tvp3-bydgoszcz': 1634239,
    'tvp3-gdansk': 1475382,
    'tvp3-gorzow-wielkopolski': 1393744,
    'tvp3-katowice': 1393798,
    'tvp3-kielce': 1393838,
    'tvp3-krakow': 1393797,
    'tvp3-lublin': 1634225,
    'tvp3-lodz': 1604263,
    'tvp3-olsztyn': 1634191,
    'tvp3-opole': 1754257,
    'tvp3-poznan': 1634308,
    'tvp3-rzeszow': 1604289,
    'tvp3-szczecin': 1604296,
    'tvp3-warszawa': 699026,
    'tvp3-wroclaw': 1634331,
    'tvpwilno': 44418549,
    'tvpalfa': 51656487
}

# Live channels of vod.tvp.pl: from kodi catchuptvandmore item_id to vod.tvp.pl live product id
VOD_LIVE_IDS = {
    'tvpabc': 399704,
    'tvpabc2': 399727,
    'tvpkryminaly': 2543050,
    'tvpmilosc': 2724087,
    'tvpmuzyka': 2999109,
    'tvpkultura': 399700,
    'tvpkobieta': 399701,
    'tvpsport': 399702,
    'tvphistoria': 399703,
    'tvpdokument': 399721,
    'tvpnauka': 399722,
    'tvprozrywka': 399724,
    'tvphistoria2': 399725,
    'tvpkultura2': 399728,
    'belsat': 399729,
    'tvpsejm': 1065594,
    'tvpsenat': 1065595,
}

# Same live products on vod.tvp.pl for the channels of CHANNEL_ID_MAP. Used when the
# channel is not (or no longer) listed on the old tvpstream page.
VOD_LIVE_FALLBACK_IDS = {
    'tvp1': 399697,
    'tvp2': 399698,
    'tvpinfo': 399699,
    'tvppolonia': 399723,
    'tvpwilno': 999687,
    'tvpworld': 399731,
    'tvpalfa': 399726,
    'tvp3-bialystok': 399732,
    'tvp3-bydgoszcz': 399740,
    'tvp3-gdansk': 399741,
    'tvp3-gorzow-wielkopolski': 399742,
    'tvp3-katowice': 399743,
    'tvp3-kielce': 399745,
    'tvp3-krakow': 399746,
    'tvp3-lodz': 399747,
    'tvp3-lublin': 399748,
    'tvp3-olsztyn': 399749,
    'tvp3-opole': 399750,
    'tvp3-poznan': 399751,
    'tvp3-rzeszow': 399752,
    'tvp3-szczecin': 399753,
    'tvp3-warszawa': 399754,
    'tvp3-wroclaw': 399755,
}

URL_VOD_LIVE_PLAYLIST = 'https://vod.tvp.pl/api/products/%s/videos/playlist'

URL_REPLAY = {
    'catalog': 'https://vod.tvp.pl/api/products/vods',
    'serial': 'https://vod.tvp.pl/api/products/vods/serials/%s/seasons/%s/episodes',
    # 'info': 'https://vod.tvp.pl/api/products/vods/{content_id}?ln={ln}&platform={pla}',
    'content': 'https://vod.tvp.pl/api/products/%s/videos/playlist',
}

# ANDROID_TV, APPLE_TV, BROWSER, ANDROID, IOS
PLATFORM = 'SMART_TV'
LANG = 'pl'
PAGE_SIZE = 100

GENERIC_HEADERS = {'User-Agent': web_utils.get_random_ua()}

# TO DO
# Add more replays


def fetch_programs():
    fetch_more_content = True
    next_itm = 0
    tvp_items = []
    while fetch_more_content:
        fetch_more_content = False
        params = {
            'firstResult': next_itm,
            'maxResults': PAGE_SIZE,
            'mainCategoryId[]': 24,
            'sort': 'createdAt',
            'order': 'desc',
            'ln': LANG,
            'platform': PLATFORM
        }
        resp = urlquick.get(URL_REPLAY['catalog'], params=params, headers=GENERIC_HEADERS, max_age=-1)
        if resp.status_code != 200:
            break
        resp_json = resp.json()
        tvp_items.extend(resp_json['items'])
        next_itm = resp_json['meta']['firstResult'] + resp_json['meta']['maxResults']
        if next_itm <= resp_json['meta']['totalCount']:
            fetch_more_content = True
    return tvp_items


@Route.register
def list_programs(plugin, item_id, **kwargs):
    tvp_items = fetch_programs()
    if tvp_items is None or len(tvp_items) == 0:
        plugin.notify(plugin.localize(30891), plugin.localize(30718), Script.NOTIFY_ERROR)
        return

    for tvp_item in tvp_items:
        item = Listitem()
        item.label = tvp_item['title']
        serial_image_url = 'https:' + tvp_item['images']['16x9'][0]['url']
        item.art['thumb'] = serial_image_url
        # item.art['fanart'] = 'resources/channels/pl/tvpvod_fanart.jpg'

        serial_id = int(tvp_item['id'])
        item.set_callback(list_episodes, serial_id=serial_id, season_id=serial_id + 1, serial_image_url=serial_image_url)
        item_post_treatment(item)
        yield item


@Route.register
def list_episodes(plugin, serial_id, season_id, serial_image_url):
    url = URL_REPLAY['serial'] % (serial_id, season_id)
    params = {
        'ln': LANG,
        'platform': PLATFORM
    }
    resp = urlquick.get(url, params=params, headers=GENERIC_HEADERS, max_age=-1)
    for tvp_episode in resp.json():
        item = Listitem()
        item.label = tvp_episode['title']
        item.art['thumb'] = 'https:' + tvp_episode['images']['16x9'][0]['url']
        item.art['fanart'] = serial_image_url

        episode_id = int(tvp_episode['id'])
        item.set_callback(play_episode, episode_id=episode_id)
        item_post_treatment(item, is_playable=True)
        yield item


@Resolver.register
def play_episode(plugin, episode_id):
    content_url = URL_REPLAY['content'] % episode_id
    params = {
        'platform': PLATFORM,
        'videoType': 'MOVIE'
    }
    content = None
    content = urlquick.get(content_url, params=params, headers=GENERIC_HEADERS, max_age=-1, )
    if content.status_code != 200:
        plugin.notify(plugin.localize(30891), plugin.localize(30718), Script.NOTIFY_ERROR)
        return False

    content_json = content.json() if content is not None else {}
    # HLS vs DASH
    m3u8_url = content_json['sources']['HLS'][0]['src']

    return resolver_proxy.get_stream_with_quality(plugin, m3u8_url)


def get_channels():
    """
    Extract the listing of channels from TVP page as a list of JSON elments.
    None if HTTP request fails or infomation moved to another place in the HTML page.
    """
    resp = urlquick.get(LIVE_MAIN_URL, headers=GENERIC_HEADERS, max_age=-1, timeout=30)
    root = resp.parse()

    channels_str = None
    for js in root.findall(".//body/script[@type='text/javascript']"):
        if js.text is not None and "window.__channels =" in js.text:
            channels_str = js.text
            channels_str = channels_str.replace("window.__channels =", "{ \"channels\": ").replace(";", "}")
            break

    if channels_str is None:
        return None

    try:
        channels = json.loads(channels_str)
        return channels.get('channels')
    except Exception:
        return None


def _get_internal_id(item_id, **kwargs):
    """Resolve the TVP3 region, if any, to the key used in CHANNEL_ID_MAP."""
    if "tvp3" == item_id:
        tvp3_region = kwargs.get('language', Script.setting['tvp3.language'])
        item_id = LIVE_TVP3_REGIONS[tvp3_region]
    return item_id


def get_channel_id(item_id, **kwargs):
    """
    Get the id of the channel in TVP page from id internal to catchuptvandmore plugin.
    TVP3 is a channel shared for every regions.
    Channel region info taken from additional parameter
    """
    return CHANNEL_ID_MAP[_get_internal_id(item_id, **kwargs)]


def _get_live_id(channels, channel_id):
    """
    Get the id of the live video broadcasted by the channel
    None if channel cannot be found or it hasn't any video / live info associated.
    """
    for channel in channels:
        if channel.get('id') == channel_id:
            if channel.get('items', None) is not None:
                for item in channel.get('items', []):
                    live_id = item.get('video_id', None)
                    if live_id is not None:
                        return live_id
    return None


def _get_live_stream_url(live_id):
    """
    Get URL to playable m3u8 of the live stream.
    None if HTTP request to get info fails or if there is no m3u8 / mpeg / hls data associated.
    """
    headers = {
        'User-Agent': web_utils.get_random_ua(),
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    url = URL_STREAMS.format(live_id=live_id)
    try:
        live_streams_url = urlquick.get(url, headers=headers, max_age=-1, timeout=30)
        live_streams = live_streams_url.json()
    except Exception:
        return None

    live_stream_status = live_streams.get('status', None)
    if live_stream_status is not None and live_stream_status != 'OK':
        return live_stream_status

    live_stream_url = None
    if live_streams.get('formats', None) is not None:
        for stream_format in live_streams.get('formats'):
            if 'application/x-mpegurl' == stream_format.get('mimeType'):
                live_stream_url = stream_format.get('url')
    return live_stream_url


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    channels = get_channels() or []

    channel_id = get_channel_id(item_id, **kwargs)
    live_id = _get_live_id(channels, channel_id)
    if live_id is None:
        # Channel not (or no longer) on the scrapped page, try vod.tvp.pl
        return _play_vod_live(plugin, VOD_LIVE_FALLBACK_IDS.get(_get_internal_id(item_id, **kwargs)))

    live_stream_url = _get_live_stream_url(live_id)
    if live_stream_url is None:
        plugin.notify('INFO', plugin.localize(30716))
        return False
    if not live_stream_url.startswith('http'):
        plugin.notify('INFO', plugin.localize(30891))
        return False

    return live_stream_url


@Resolver.register
def get_vod_live_url(plugin, item_id, **kwargs):
    """Play a live channel of vod.tvp.pl (FAST and thematic channels)."""
    return _play_vod_live(plugin, VOD_LIVE_IDS.get(item_id))


def _play_vod_live(plugin, live_id):
    if live_id is None:
        plugin.notify('INFO', plugin.localize(30716))
        return False

    headers = {'User-Agent': web_utils.get_random_ua()}
    try:
        resp = urlquick.get(URL_VOD_LIVE_PLAYLIST % live_id,
                            params={'videoType': 'LIVE', 'lang': 'PL', 'platform': 'BROWSER'},
                            headers=headers, max_age=-1, timeout=30)
        data = resp.json()
    except Exception:
        plugin.notify('INFO', plugin.localize(30716))
        return False

    sources = data.get('sources') or {}
    drm = data.get('drm') or {}
    widevine = (drm.get('WIDEVINE') or {}).get('src')
    if widevine and sources.get('DASH'):
        # Protected stream
        return resolver_proxy.get_stream_with_quality(
            plugin, video_url=sources['DASH'][0]['src'], manifest_type='mpd',
            license_url=widevine, headers=headers)
    if sources.get('HLS'):
        return resolver_proxy.get_stream_with_quality(
            plugin, video_url=sources['HLS'][0]['src'], manifest_type='hls', headers=headers)
    if sources.get('DASH'):
        return resolver_proxy.get_stream_with_quality(
            plugin, video_url=sources['DASH'][0]['src'], manifest_type='mpd', headers=headers)

    plugin.notify('INFO', plugin.localize(30716))
    return False
