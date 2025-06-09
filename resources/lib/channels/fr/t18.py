# -*- coding: utf-8 -*-
# Copyright: (c) 2018, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import re

from codequick import Resolver
import urlquick

from resources.lib import resolver_proxy, web_utils

URL_ROOT = 'https://t18.fr/'


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    resp = urlquick.get(
        URL_ROOT, headers={"User-Agent": web_utils.get_random_ua()}, max_age=-1)
    live_id = re.compile(r'"https://geo.dailymotion.com/player.html\?video=(.*?)[\?\"]').findall(resp.text)[0]
    embedder = "https://t18.fr/"
    return resolver_proxy.get_stream_dailymotion(plugin,
                                                 live_id,
                                                 download_mode=False,
                                                 embeder=embedder)
