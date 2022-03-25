# -*- coding: utf-8 -*-
# Copyright: (c) 2019, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import re

# noinspection PyUnresolvedReferences
from codequick import Resolver, Route
# noinspection PyUnresolvedReferences
from codequick.utils import urljoin_partial
import urlquick

from resources.lib import resolver_proxy
from resources.lib.web_utils import get_random_ua

URL_ROOT = 'https://www.antennecentre.tv/'
url_constructor = urljoin_partial(URL_ROOT)
URL_LIVE = url_constructor('direct')

URL_STREAM = 'https://actv.fcst.tv/player/embed/%s'

PATTERN_PLAYER = re.compile(r'actv\.fcst\.tv/player/embed/(.*?)\?')
PATTERN_STREAM = re.compile(r'file\":\"(.*?)\"')


@Route.register
def list_programs(plugin, item_id, **kwargs):
    # TODO Add Replay
    pass


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    resp = urlquick.get(URL_LIVE, max_age=-1)
    live_id = PATTERN_PLAYER.findall(resp.text)[0]

    headers = {
        "User-Agent": get_random_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "iframe",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "referrer": URL_ROOT
    }

    resp2 = urlquick.get(URL_STREAM % live_id, headers=headers, max_age=-1)
    list_files = PATTERN_STREAM.findall(resp2.text)
    url_stream = None
    for stream_data in list_files:
        if 'm3u8' in stream_data:
            url_stream = stream_data.replace("\\", "")

    if url_stream is None:
        return False

    return resolver_proxy.get_stream_with_quality(plugin, video_url=url_stream, manifest_type="hls")
