
# -*- coding: utf-8 -*-
# Copyright: (c) 2017, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import re
import json
import urlquick

# noinspection PyUnresolvedReferences
from codequick import Resolver

from resources.lib import resolver_proxy, web_utils

URL_LIVES = 'https://www.telemaroc.tv/liveTV'
STREAM_INFO_URL = 'https://player-api.new.livestream.com/accounts/%s/events/%s/stream_info'

GENERIC_HEADERS = {"User-Agent": web_utils.get_random_ua()}


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    resp = urlquick.get(URL_LIVES, headers=GENERIC_HEADERS, max_age=-1)
    root = resp.parse()
    for script in root.iterfind('.//script'):
        if script.get('data-embed_id') is not None:
            embed_id = script.get('data-embed_id')
            for frame in root.iterfind('.//frame'):
                if frame.get('id') is not None:
                    if frame.get('id') == embed_id:
                        src = frame.get('src')
                        accout_id = re.compile(r'accounts\/(.*)\/events').findall(src)[0]
                        event_id = re.compile(r'events\/(.*)\/player').findall(src)[0]
                        info_url = STREAM_INFO_URL % (accout_id, event_id)
                        j_parser = urlquick.get(info_url, headers=GENERIC_HEADERS, max_age=-1).json()
                        video_url = j_parser['secure_m3u8_url']
                        return resolver_proxy.get_stream_with_quality(plugin, video_url)
