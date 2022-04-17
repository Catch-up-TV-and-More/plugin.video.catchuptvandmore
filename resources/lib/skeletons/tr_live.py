# -*- coding: utf-8 -*-
# Copyright: (c) 2022, itasli
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
    'fox': {
        'resolver': '/resources/lib/channels/tr/fox:get_live_url',
        'label': 'FOX',
        'thumb': 'channels/tr/fox.png',
        'fanart': 'channels/tr/fox_fanart.jpg',
        'enabled': True,
        'order': 1
    },
    'kanal7': {
        'resolver': '/resources/lib/channels/tr/kanal7:get_live_url',
        'label': 'Kanal 7',
        'thumb': 'channels/tr/kanal7.png',
        'fanart': 'channels/tr/kanal7_fanart.jpg',
        'enabled': True,
        'order': 2
    },
    'kanald': {
        'resolver': '/resources/lib/channels/tr/kanald:get_live_url',
        'label': 'Kanal D',
        'thumb': 'channels/tr/kanald.png',
        'fanart': 'channels/tr/kanald_fanart.jpg',
        'enabled': True,
        'order': 3
    },
    'show': {
        'resolver': '/resources/lib/channels/tr/show:get_live_url',
        'label': 'Show TV',
        'thumb': 'channels/tr/show.png',
        'fanart': 'channels/tr/show_fanart.jpg',
        'enabled': True,
        'order': 4
    },
    'showmax': {
        'resolver': '/resources/lib/channels/tr/showmax:get_live_url',
        'label': 'ShowMax TV',
        'thumb': 'channels/tr/showmax.png',
        'fanart': 'channels/tr/showmax_fanart.jpg',
        'enabled': True,
        'order': 5
    },
    'star': {
        'resolver': '/resources/lib/channels/tr/star:get_live_url',
        'label': 'Star TV',
        'thumb': 'channels/tr/star.png',
        'fanart': 'channels/tr/star_fanart.jpg',
        'enabled': True,
        'order': 6
    },
    'tv8': {
        'resolver': '/resources/lib/channels/tr/tv8:get_live_url',
        'label': 'TV 8',
        'thumb': 'channels/tr/tv8.png',
        'fanart': 'channels/tr/tv8_fanart.jpg',
        'enabled': True,
        'order': 7
    },
}
