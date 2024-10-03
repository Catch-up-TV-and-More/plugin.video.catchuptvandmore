# -*- coding: utf-8 -*-
# Copyright: (c) 2019, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import re

from codequick import Resolver
import urlquick

from resources.lib import resolver_proxy, web_utils

# TODO
# Add Replay

URL_ROOT = "https://www.sportenfrance.com"

GENERIC_HEADERS = {"User-Agent": web_utils.get_random_ua()}


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    try:
        resp = urlquick.get(URL_ROOT, headers=GENERIC_HEADERS, max_age=-1)
        root = resp.parse()
        for live_datas in root.iterfind('.//div'):
            if live_datas.get('id') is not None:
                live_id = re.compile('player_(.*?)$').findall(live_datas.get('id'))[0]
                return resolver_proxy.get_stream_dailymotion(plugin, live_id)

    except Exception:
        return resolver_proxy.get_stream_dailymotion(plugin, 'x8sayn8')
