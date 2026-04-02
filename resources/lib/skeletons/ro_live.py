# -*- coding: utf-8 -*-
# Copyright: (c) 2025, QValette
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

# The following dictionaries describe
# the addon's tree architecture.
# * Key: item id
# * Value: item infos
#    - route (folder)/resolver (playable URL): Callback function to run once this item is selected
#    - thumb: Item thumb path relative to "media" folder
#    - fanart: Item fanart path relative to "media" folder

root = 'live_tv'

menu = {
    'antena1': {
        'resolver': '/resources/lib/channels/ro/antena:get_live_url',
        'label': 'Antena 1',
        'thumb': 'channels/ro/antena1.png',
        'fanart': 'channels/ro/antena_fanart.jpg',
        'xmltv_id': 'Antena1.ro@SD',
        'm3u_group': 'Antena Play',
        'enabled': True,
        'order': 1
    },
    'comedy-play': {
        'resolver': '/resources/lib/channels/ro/antena:get_live_url',
        'label': 'Comedy Play',
        'thumb': 'channels/ro/comedy_play.png',
        'fanart': 'channels/ro/antena_fanart.jpg',
        'xmltv_id': 'ComedyPlay.ro@SD',
        'm3u_group': 'Antena Play',
        'enabled': True,
        'order': 2
    },
    'observator-news': {
        'resolver': '/resources/lib/channels/ro/antena:get_live_url',
        'label': 'Observator News',
        'thumb': 'channels/ro/observator_news.png',
        'fanart': 'channels/ro/antena_fanart.jpg',
        'xmltv_id': 'ObservatorNews.ro@SD',
        'm3u_group': 'Antena Play',
        'enabled': True,
        'order': 3
    },
    'atomic-academy': {
        'resolver': '/resources/lib/channels/ro/atomic:get_live_url',
        'label': 'Atomic Academy TV',
        'thumb': 'channels/ro/atomic_academy.png',
        'fanart': 'channels/ro/atomic_fanart.jpg',
        'xmltv_id': 'AtomicAcademyTV.ro@SD',
        'm3u_group': 'Atomic',
        'enabled': True,
        'order': 4
    },
    'atomic-tv': {
        'resolver': '/resources/lib/channels/ro/atomic:get_live_url',
        'label': 'Atomic TV',
        'thumb': 'channels/ro/atomic_tv.png',
        'fanart': 'channels/ro/atomic_fanart.jpg',
        'xmltv_id': 'AtomicTV.ro@SD',
        'm3u_group': 'Atomic',
        'enabled': True,
        'order': 5
    },
    'banat-tv': {
        'resolver': '/resources/lib/channels/ro/regional:get_live_url',
        'label': 'Banat TV',
        'thumb': 'channels/ro/banat_tv.png',
        'fanart': 'channels/ro/banat_tv_fanart.jpg',
        'xmltv_id': 'BanatTV.ro@SD',
        'm3u_group': 'Regional',
        'enabled': True,
        'order': 6
    },
    'protv-news': {
        'resolver': '/resources/lib/channels/ro/protvnews:get_live_url',
        'label': 'Pro TV News',
        'thumb': 'channels/ro/protv_news.png',
        'fanart': 'channels/ro/protv_news_fanart.jpg',
        'xmltv_id': 'PROTVNews.ro@SD',
        'm3u_group': 'Pro TV',
        'enabled': True,
        'order': 7
    },
}