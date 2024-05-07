# -*- coding: utf-8 -*-
# Copyright: (c) 2024, JimmyGilles
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

# The following dictionaries describe
# the addon's tree architecture.
# * Key: item id
# * Value: item infos
#     - route (folder)/resolver (playable URL): Callback function to run once this item is selected
#     - thumb: Item thumb path relative to "media" folder
#     - fanart: Item fanart path relative to "media" folder

root = 'live_tv'

menu = {
    'bolivia_tv': {
        'resolver': '/resources/lib/channels/bo/boliviatv:get_live_url',
        'label': 'Bolivia TV',
        'thumb': 'channels/bo/boliviatv.png',
        'fanart': 'channels/bo/boliviatv_fanart.jpg',
        'm3u_group': 'Bolivia',
        'enabled': True,
        'order': 1
    },
}