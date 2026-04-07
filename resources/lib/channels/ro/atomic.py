# -*- coding: utf-8 -*-
# Copyright: (c) 2025, QValette
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import re

# noinspection PyUnresolvedReferences
from codequick import Resolver

import urlquick

from resources.lib import resolver_proxy

URL_ROOT = 'https://atomic.streamnet.ro/'

# Order on the page: atomic-tv first, atomic-academy second
CHANNEL_ORDER = ['atomic-tv', 'atomic-academy']


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    resp = urlquick.get(URL_ROOT, max_age=-1)
    sources = re.findall(r'<source[^>]+src=["\']([^"\']+)["\']', resp.text)
    urls = dict(zip(CHANNEL_ORDER, sources))
    return resolver_proxy.get_stream_with_quality(plugin, urls[item_id])
