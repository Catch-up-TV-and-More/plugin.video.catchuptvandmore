# -*- coding: utf-8 -*-
# Copyright: (c) 2025, QValette
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

# noinspection PyUnresolvedReferences
from codequick import Resolver

from resources.lib import resolver_proxy

URL_LIVE = {
    'antena1': 'https://live1ag.antenaplay.ro/live_a1ro/live_a1ro.m3u8',
    'comedy-play': 'https://stream1.antenaplay.ro/live/ComedyPlay/playlist.m3u8',
    'observator-news': 'https://live1ag.antenaplay.ro/live_ObservatorNews/live_ObservatorNews.m3u8',
}


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    return resolver_proxy.get_stream_with_quality(plugin, URL_LIVE[item_id])