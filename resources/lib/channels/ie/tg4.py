# -*- coding: utf-8 -*-
# Copyright: (c) 2025
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import re
import urlquick
from codequick import Resolver

from resources.lib import resolver_proxy

URL_ROOT = 'https://www.tg4.ie'

URL_LIVE = URL_ROOT + '/en/player/watch-live/home'


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    html_text = urlquick.get(URL_LIVE, max_age=-1).text

    data_video_id = re.search(
        r'if\s*\(\s*getCookie\("GeoCountry"\)\s*==\s*"IE"\s*\)\s*{\s*VideoID\s*=\s*(\d+);',
        html_text,
        re.DOTALL
    ).group(1)

    data_account = re.search(
        r"setAttribute\(\s*['\"]data-account['\"]\s*,\s*(\d+)\s*\)",
        html_text
    ).group(1)

    data_player = re.search(
        r"setAttribute\(\s*['\"]data-player['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)",
        html_text
    ).group(1)

    return resolver_proxy.get_brightcove_video_json(plugin, data_account=data_account, data_video_id=data_video_id,
                                                    data_player=data_player)
