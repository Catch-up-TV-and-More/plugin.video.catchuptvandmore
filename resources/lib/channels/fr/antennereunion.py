# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2018  SylvainCecchetto

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

from codequick import Route, Resolver, Listitem, utils, Script

from resources.lib.labels import LABELS

from resources.lib import web_utils

import re
import urlquick

'''
TODO Add Replay
'''

'''
TODO Add Replay
'''

URL_ROOT = 'http://www.antennereunion.fr'

URL_LIVE = URL_ROOT + '/direct'


def live_entry(plugin, item_id, item_dict):
    return get_live_url(plugin, item_id, item_id.upper(), item_dict)


@Resolver.register
def get_live_url(plugin, item_id, video_id, item_dict):

    live_html = urlquick.get(
        URL_LIVE,
        headers={'User-Agent': web_utils.get_random_ua},
        max_age=-1)
    list_url_stream = re.compile(
        r'file"\: "(.*?)"').findall(
            live_html.text)
    url_live = ''
    for url_stream_data in list_url_stream:
        if 'm3u8' in url_stream_data:
            url_live = url_stream_data
    return url_live
