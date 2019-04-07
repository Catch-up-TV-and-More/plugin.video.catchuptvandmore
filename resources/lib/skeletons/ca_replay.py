# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2016  SylvainCecchetto

    This file is part of Catch-up TV & More.

    Catch-up TV & More is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    Catch-up TV & More is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with Catch-up TV & More; if not, write to the Free Software Foundation,
    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

# The unicode_literals import only has
# an effect on Python 2.
# It makes string literals as unicode like in Python 3
from __future__ import unicode_literals
from codequick import Script


"""
The following dictionaries describe
the addon's tree architecture.
* Key: item id
* Value: item infos
    - callback: Callback function to run once this item is selected
    - thumb: Item thumb path relative to "media" folder
    - fanart: Item fanart path relative to "meia" folder
    - module: Item module to load in order to work (like 6play.py)
"""

menu = {
    'tva': {
        'callback': 'replay_bridge',
        'thumb': 'channels/ca/tva.png',
        'fanart': 'channels/ca/tva_fanart.jpg',
        'module': 'resources.lib.channels.ca.tva'
    },
    'tv5': {
        'callback': 'replay_bridge',
        'thumb': 'channels/ca/tv5.png',
        'fanart': 'channels/ca/tv5_fanart.jpg',
        'module': 'resources.lib.channels.ca.tv5'
    },
    'unis': {
        'callback': 'replay_bridge',
        'thumb': 'channels/ca/unis.png',
        'fanart': 'channels/ca/unis_fanart.jpg',
        'module': 'resources.lib.channels.ca.tv5'
    },
    'telequebec': {
        'callback': 'replay_bridge',
        'thumb': 'channels/ca/telequebec.png',
        'fanart': 'channels/ca/telequebec_fanart.jpg',
        'module': 'resources.lib.channels.ca.telequebec'
    },
    'icitoutv': {
        'callback': 'replay_bridge',
        'thumb': 'channels/ca/icitoutv.png',
        'fanart': 'channels/ca/icitoutv_fanart.jpg',
        'module': 'resources.lib.channels.ca.icitoutv'
    },
    'icitele': {
        'callback': 'replay_bridge',
        'thumb': 'channels/ca/icitele.png',
        'fanart': 'channels/ca/icitele_fanart.jpg',
        'module': 'resources.lib.channels.ca.icitele'
    },
    'telemag': {
        'callback': 'replay_bridge',
        'thumb': 'channels/ca/telemag.png',
        'fanart': 'channels/ca/telemag_fanart.jpg',
        'module': 'resources.lib.channels.ca.telemag'
    }
}
