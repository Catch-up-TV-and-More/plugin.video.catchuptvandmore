# -*- coding: utf-8 -*-
# Copyright: (c) 2024, JimmyGilles
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import re

import urlquick
# noinspection PyUnresolvedReferences
from codequick import Resolver, Route
# noinspection PyUnresolvedReferences
from codequick.utils import urljoin_partial

from resources.lib import resolver_proxy, web_utils

URL_ROOT = 'https://www.boliviatv.bo/'
url_constructor = urljoin_partial(URL_ROOT)
URL_LIVE = url_constructor('principal/vivo71.php')
PATTERN_VIDEO_M3U8 = re.compile(r'file: \"(.*?\.m3u8.*)\"')

GENERIC_HEADERS = {"User-Agent": web_utils.get_random_ua()}


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    resp = urlquick.get(URL_LIVE, headers=GENERIC_HEADERS, max_age=-1)
    frame_url = resp.parse("iframe").get('src')
    resp = urlquick.get(frame_url, headers=GENERIC_HEADERS, max_age=-1)

    m3u8_array = PATTERN_VIDEO_M3U8.findall(resp.text)
    if len(m3u8_array) == 0:
        return False
    video_url = m3u8_array[0].replace("\\", "")

    return resolver_proxy.get_stream_with_quality(plugin, video_url=video_url)
