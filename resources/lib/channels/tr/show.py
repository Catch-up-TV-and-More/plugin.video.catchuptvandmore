# -*- coding: utf-8 -*-
# Copyright: (c) 2018, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import json

from codequick import Resolver
import urlquick

from resources.lib import resolver_proxy


# TODO

URL_ROOT = 'https://www.showtv.com.tr'

URL_LIVE = URL_ROOT + '/canli-yayin'


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    """Get video URL and start video player"""
    resp = urlquick.get(URL_LIVE)
    root = resp.parse()

    for live in root.iterfind(".//div[@class='htplay_video']"):
        res = json.loads(live.attrib['data-ht'])
    
    return res['ht_stream_m3u8']