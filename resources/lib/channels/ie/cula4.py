# -*- coding: utf-8 -*-
# Copyright: (c) 2025
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import urlquick
from codequick import Resolver

from resources.lib import resolver_proxy


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    return resolver_proxy.get_brightcove_video_json(plugin, data_account='1555966122001', data_video_id='6383455473112',
                                                    data_player='iAWGFfVCr', headers={'origin': 'https://cula4.com',
                                                                                      'referer': 'https://cula4.com'})