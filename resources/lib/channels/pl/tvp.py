# -*- coding: utf-8 -*-
# Copyright: (c) 2018, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import json
import urlquick

from codequick import Resolver, Script
from resources.lib import web_utils


# TO DO
# Add Replay

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
    'ua1': 58759123,
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


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    tvp3_region = kwargs.get('language', Script.setting['tvp3.language'])

    resp = urlquick.get(
        LIVE_MAIN_URL, headers={'User-Agent': web_utils.get_random_ua()},
        max_age=-1, timeout=30)
    root = resp.parse()

    channels_str = None
    for js in root.findall(".//body/script[@type='text/javascript']"):
        if js.text is not None and "window.__channels =" in js.text:
            channels_str = js.text
            channels_str = channels_str.replace("window.__channels =", "{ \"channels\": ").replace(";", "}")
            break

    if channels_str is None:
        # Stream is not available - channel not found on scrapped page
        plugin.notify('INFO', plugin.localize(30716))
        return False

    try:
        channels = json.loads(channels_str)
    except Exception as error:
        plugin.notify('INFO', plugin.localize(30716))
        return False


    live_id = None
    for channel in channels.get('channels'):
        # TVP3 is a channel shared for every regions.
        # channel region info taken from additional parameter
        if "tvp3" == item_id:
            item_id = LIVE_TVP3_REGIONS[tvp3_region]
        # Get live video information from selected channel
        if CHANNEL_ID_MAP[item_id] == channel.get('id'):
            print('poloniachannel', channel)
            if channel.get('items', None) is not None:
                for item in channel.get('items', []):
                    live_id = item.get('video_id', None)
                    if live_id is not None:
                        break

    if live_id is None:
        # Stream is not available - channel not found on scrapped page
        plugin.notify('INFO', plugin.localize(30716))
        return False

    try:
        live_streams_url = urlquick.get(
            URL_STREAMS.format(live_id=live_id), headers={
                'User-Agent': web_utils.get_random_ua(),
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br'
            },
            max_age=-1, timeout=30)
        live_streams = live_streams_url.json()
    except Exception as error:
        plugin.notify('INFO', plugin.localize(30716))
        return False

    live_stream_url = None
    if live_streams.get('formats', None) is not None:
        for stream_format in live_streams.get('formats'):
            if 'application/x-mpegurl' == stream_format.get('mimeType'):
                live_stream_url = stream_format.get('url')

    if live_stream_url is None:
        plugin.notify('INFO', plugin.localize(30716))
        return False

    return live_stream_url
