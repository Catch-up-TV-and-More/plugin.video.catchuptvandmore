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

from resources.lib import resolver_proxy

URL_ROOT = 'https://www.boliviatv.bo/'
url_constructor = urljoin_partial(URL_ROOT)
URL_LIVE = url_constructor('principal/vivo71.php')
PATTERN_VIDEO_M3U8 = re.compile(r'file: \"(.*?\.m3u8.*)\"')

@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    resp = urlquick.get(URL_LIVE, max_age=-1)
    root_elem = resp.parse("iframe")
    frame_url = root_elem.get('src')
    resp2 = urlquick.get(frame_url, max_age=-1)

    m3u8_array = PATTERN_VIDEO_M3U8.findall(resp2.text)
    if len(m3u8_array) == 0:
        return False
    video_url = m3u8_array[0].replace("\\", "")

    return resolver_proxy.get_stream_with_quality(plugin, video_url=video_url, manifest_type="hls")
