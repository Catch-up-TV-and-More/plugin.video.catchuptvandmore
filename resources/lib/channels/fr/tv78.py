# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Joaopa
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import re

from codequick import Resolver
import urlquick


from resources.lib import resolver_proxy, web_utils

URL_ROOT = 'https://www.tv78.com'
URL_LIVE = URL_ROOT + '/webtv'


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    resp = urlquick.get(URL_LIVE, headers={'User-Agent': web_utils.get_random_ua()}, max_age=-1)
    root = resp.parse()
    video_url = root.find('.//source').get('src')

    return resolver_proxy.get_stream_with_quality(plugin, video_url, manifest_type="hls")
