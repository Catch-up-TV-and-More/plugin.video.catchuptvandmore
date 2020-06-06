# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2017  SylvainCecchetto

    This file is part of Catch-up TV & More.

    Catch-up TV & More is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    Catch-up TV & More is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with Catch-up TV & More; if not, write to the Free Software Foundation,
    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

# The unicode_literals import only has
# an effect on Python 2.
# It makes string literals as unicode like in Python 3
from __future__ import unicode_literals

import re

from resources.lib.codequick import Route, Resolver, Listitem, utils, Script
from resources.lib import urlquick

# Source: https://ethiov.com/live-channels


@Resolver.register
def live_entry(plugin, item_id, **kwargs):
    urls = {
        'ectv': 'http://video2b.vixtream.net/tv/v/ectv',
        'amma': 'http://video2b.vixtream.net/tv/v/amma',
        'fbctv': 'http://video2b.vixtream.net/tv/v/fbctv',
        'walta': 'http://video2b.vixtream.net/tv/v/walta',
        'etvz': 'http://video2b.vixtream.net/tv/v/etvz',
        'etvm': 'http://video2b.vixtream.net/tv/v/etvm',
        'etvq': 'http://video2b.vixtream.net/tv/v/etvq',
        'ltv': 'http://video2b.vixtream.net/tv/v/ltv',
        'arts': 'http://video2b.vixtream.net/tv/v/arts',
        'moe': 'http://video2b.vixtream.net/tv/v/moe',
        'nahoo': 'http://video2b.vixtream.net/tv/v/nahoo',
        'obn': 'http://video2b.vixtream.net/tv/v/obn',
        'obs': 'http://video2b.vixtream.net/tv/v/obs',
        'tigrai': 'http://video2b.vixtream.net/tv/v/tigrai',
        'jtv': 'http://video2b.vixtream.net/tv/v/jtv',
        'esat': 'http://video2b.vixtream.net/tv/v/esat',
        'omn': 'http://video2b.vixtream.net/tv/v/omn',
        'aleph': 'http://video2b.vixtream.net/tv/v/aleph',
        'bisrat': 'http://video2b.vixtream.net/tv/v/bisrat',
        'onn': 'http://video2b.vixtream.net/tv/v/onn',
        'dws': 'http://video2b.vixtream.net/tv/v/dws',
        'adis': 'http://video2b.vixtream.net/tv/v/adis',
        'estv': 'http://video2b.vixtream.net/tv/v/estv',
        'south': 'http://video2b.vixtream.net/tv/v/south',
        'eritr': 'http://video2b.vixtream.net/tv/v/eritr',
        'afri': 'http://video2b.vixtream.net/tv/v/afri',
        'asham': 'http://video2b.vixtream.net/tv/v/asham',
        'ahadu': 'http://video2b.vixtream.net/tv/v/ahadu',
        'balage': 'http://video2b.vixtream.net/tv/v/balage',
        'ava': 'http://video2b.vixtream.net/tv/v/ava',
        'asrat': 'http://video2b.vixtream.net/tv/v/asrat',
        'holys': 'http://video2b.vixtream.net/tv/v/holys',
        'gloryg': 'http://video2b.vixtream.net/tv/v/gloryg'
    }
    html = urlquick.get(urls[item_id]).text.encode('utf-8')
    m3u8_url = re.compile(r'var src=\'(.*?)\';').findall(html)
    if m3u8_url:
        m3u8_url = m3u8_url[0]
    else:
        return False
    root_url = m3u8_url.split('playlist.m3u8')[0]
    m3u8_text = urlquick.get(m3u8_url).text.encode('utf-8')

    working_stream = []

    # First m3u8 file contains other m3u8 links with diferent bandwidth/resoltuion
    # but some of them returns 404 error
    # We need to check and only select streams that works
    # Else, Kodi fail if at least one stream returns 404 error
    # (instead of ignore this stream and take another one...)
    for line in m3u8_text.splitlines():
        if '#EXT' not in line:
            url = root_url + line
            try:
                r = urlquick.get(root_url + line, max_age=-1)
                if r.status_code != 404:
                    working_stream.append(url)
            except Exception:
                pass

    if working_stream:
        # TODO: Select stream based on 'prefered quality' setting
        # need to check bandwich value
        return working_stream[0]
    else:
        return False
