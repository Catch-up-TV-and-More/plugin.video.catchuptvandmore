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
    '24tv': {
        'resolver': '/resources/lib/channels/tr/24tv:get_live_url',
        'label': '360 TV',
        'thumb': 'channels/tr/24.png',
        'fanart': 'channels/tr/24_fanart.jpg',
        'enabled': True,
        'order': 1
    },
    '360tv': {
        'resolver': '/resources/lib/channels/tr/360tv:get_live_url',
        'label': '360 TV',
        'thumb': 'channels/tr/360.png',
        'fanart': 'channels/tr/360_fanart.jpg',
        'enabled': True,
        'order': 2
    },
    'ahaberhd': {
        'resolver': '/resources/lib/channels/tr/atv:get_live_url',
        'label': 'A Haber',
        'thumb': 'channels/tr/ahaber.png',
        'fanart': 'channels/tr/ahaber_fanart.jpg',
        'enabled': True,
        'order': 3
    },
    'aparahd': {
        'resolver': '/resources/lib/channels/tr/atv:get_live_url',
        'label': 'A Para',
        'thumb': 'channels/tr/apara.png',
        'fanart': 'channels/tr/apara_fanart.jpg',
        'enabled': True,
        'order': 4
    },
    'asporhd': {
        'resolver': '/resources/lib/channels/tr/atv:get_live_url',
        'label': 'A Spor',
        'thumb': 'channels/tr/aspor.png',
        'fanart': 'channels/tr/aspor_fanart.jpg',
        'enabled': True,
        'order': 5
    },
    'atvhd': {
        'resolver': '/resources/lib/channels/tr/atv:get_live_url',
        'label': 'atv',
        'thumb': 'channels/tr/atv.png',
        'fanart': 'channels/tr/atv_fanart.jpg',
        'enabled': True,
        'order': 6
    },
    'a2tv': {
        'resolver': '/resources/lib/channels/tr/atv:get_live_url',
        'label': 'a2',
        'thumb': 'channels/tr/a2.png',
        'fanart': 'channels/tr/a2_fanart.jpg',
        'enabled': True,
        'order': 7
    },
    'beyaz': {
        'resolver': '/resources/lib/channels/tr/beyaz:get_live_url',
        'label': 'Beyaz TV',
        'thumb': 'channels/tr/beyaz.png',
        'fanart': 'channels/tr/beyaz_fanart.jpg',
        'enabled': True,
        'order': 8
    },
    'bloomberght': {
        'resolver': '/resources/lib/channels/tr/bloomberght:get_live_url',
        'label': 'Bloomberg HT',
        'thumb': 'channels/tr/bloomberght.png',
        'fanart': 'channels/tr/bloomberght_fanart.jpg',
        'enabled': True,
        'order': 9
    },
    'cine5': {
        'resolver': '/resources/lib/channels/tr/cine5:get_live_url',
        'label': 'Cine5',
        'thumb': 'channels/tr/cine5.png',
        'fanart': 'channels/tr/cine5_fanart.jpg',
        'enabled': True,
        'order': 10
    },
    'cnnturk': {
        'resolver': '/resources/lib/channels/tr/cnnturk:get_live_url',
        'label': 'CNN TURK',
        'thumb': 'channels/tr/cnnturk.png',
        'fanart': 'channels/tr/cnnturk_fanart.jpg',
        'enabled': True,
        'order': 11
    },
    'fox': {
        'resolver': '/resources/lib/channels/tr/fox:get_live_url',
        'label': 'FOX',
        'thumb': 'channels/tr/fox.png',
        'fanart': 'channels/tr/fox_fanart.jpg',
        'enabled': True,
        'order': 12
    },
    'haberglobal': {
        'resolver': '/resources/lib/channels/tr/haberglobal:get_live_url',
        'label': 'Haber Global',
        'thumb': 'channels/tr/haberglobal.png',
        'fanart': 'channels/tr/haberglobal_fanart.jpg',
        'enabled': True,
        'order': 13
    },
    'haberturk': {
        'resolver': '/resources/lib/channels/tr/haberturk:get_live_url',
        'label': 'Haberturk',
        'thumb': 'channels/tr/haberturk.png',
        'fanart': 'channels/tr/haberturk_fanart.jpg',
        'enabled': True,
        'order': 14
    },
    'kanal7': {
        'resolver': '/resources/lib/channels/tr/kanal7:get_live_url',
        'label': 'Kanal 7',
        'thumb': 'channels/tr/kanal7.png',
        'fanart': 'channels/tr/kanal7_fanart.jpg',
        'enabled': True,
        'order': 15
    },
    'kanald': {
        'resolver': '/resources/lib/channels/tr/kanald:get_live_url',
        'label': 'Kanal D',
        'thumb': 'channels/tr/kanald.png',
        'fanart': 'channels/tr/kanald_fanart.jpg',
        'enabled': True,
        'order': 16
    },
    'minikagococuk': {
        'resolver': '/resources/lib/channels/tr/atv:get_live_url',
        'label': 'Minika Çocuk',
        'thumb': 'channels/tr/minikacocuk.png',
        'fanart': 'channels/tr/minikacocuk_fanart.jpg',
        'enabled': True,
        'order': 17
    },
    'minikago': {
        'resolver': '/resources/lib/channels/tr/atv:get_live_url',
        'label': 'Minika Go',
        'thumb': 'channels/tr/minikago.png',
        'fanart': 'channels/tr/minikago_fanart.jpg',
        'enabled': True,
        'order': 18
    },
    'ntv': {
        'resolver': '/resources/lib/channels/tr/ntv:get_live_url',
        'label': 'NTV',
        'thumb': 'channels/tr/ntv.png',
        'fanart': 'channels/tr/ntv_fanart.jpg',
        'enabled': True,
        'order': 19
    },
    'show': {
        'resolver': '/resources/lib/channels/tr/show:get_live_url',
        'label': 'Show TV',
        'thumb': 'channels/tr/show.png',
        'fanart': 'channels/tr/show_fanart.jpg',
        'enabled': True,
        'order': 20
    },
    'showmax': {
        'resolver': '/resources/lib/channels/tr/showmax:get_live_url',
        'label': 'ShowMax TV',
        'thumb': 'channels/tr/showmax.png',
        'fanart': 'channels/tr/showmax_fanart.jpg',
        'enabled': True,
        'order': 21
    },
    'star': {
        'resolver': '/resources/lib/channels/tr/star:get_live_url',
        'label': 'Star TV',
        'thumb': 'channels/tr/star.png',
        'fanart': 'channels/tr/star_fanart.jpg',
        'enabled': True,
        'order': 22
    },
    'tele1': {
        'resolver': '/resources/lib/channels/tr/tele1:get_live_url',
        'label': 'Tele 1',
        'thumb': 'channels/tr/tele1.png',
        'fanart': 'channels/tr/tele1_fanart.jpg',
        'enabled': True,
        'order': 23
    },
    'teve2': {
        'resolver': '/resources/lib/channels/tr/teve2:get_live_url',
        'label': 'Teve2',
        'thumb': 'channels/tr/teve2.png',
        'fanart': 'channels/tr/teve2_fanart.jpg',
        'enabled': True,
        'order': 24
    },
    'trt1': {
        'resolver': '/resources/lib/channels/tr/trt:get_live_url',
        'label': 'TRT 1',
        'thumb': 'channels/tr/trt1.png',
        'fanart': 'channels/tr/trt1_fanart.jpg',
        'enabled': True,
        'order': 25
    },
    'trt2': {
        'resolver': '/resources/lib/channels/tr/trt:get_live_url',
        'label': 'TRT 2',
        'thumb': 'channels/tr/trt2.png',
        'fanart': 'channels/tr/trt2_fanart.jpg',
        'enabled': True,
        'order': 26
    },
    'trtavaz': {
        'resolver': '/resources/lib/channels/tr/trt:get_live_url',
        'label': 'TRT Avaz',
        'thumb': 'channels/tr/trtavaz.png',
        'fanart': 'channels/tr/trtavaz_fanart.jpg',
        'enabled': True,
        'order': 27
    },
    'trtbelgesel': {
        'resolver': '/resources/lib/channels/tr/trt:get_live_url',
        'label': 'TRT Belgesel',
        'thumb': 'channels/tr/trtbelgesel.png',
        'fanart': 'channels/tr/trtbelgesel_fanart.jpg',
        'enabled': True,
        'order': 28
    },
    'trtcocuk': {
        'resolver': '/resources/lib/channels/tr/trt:get_live_url',
        'label': 'TRT Çocuk',
        'thumb': 'channels/tr/trtcocuk.png',
        'fanart': 'channels/tr/trtcocuk_fanart.jpg',
        'enabled': True,
        'order': 29
    },
    'trthaber': {
        'resolver': '/resources/lib/channels/tr/trt:get_live_url',
        'label': 'TRT Haber',
        'thumb': 'channels/tr/trthaber.png',
        'fanart': 'channels/tr/trthaber_fanart.jpg',
        'enabled': True,
        'order': 30
    },
    'tv5': {
        'resolver': '/resources/lib/channels/tr/tv5:get_live_url',
        'label': 'TV 5',
        'thumb': 'channels/tr/tv5.png',
        'fanart': 'channels/tr/tv5_fanart.jpg',
        'enabled': True,
        'order': 31
    },
    'tv8': {
        'resolver': '/resources/lib/channels/tr/tv8:get_live_url',
        'label': 'TV 8',
        'thumb': 'channels/tr/tv8.png',
        'fanart': 'channels/tr/tv8_fanart.jpg',
        'enabled': True,
        'order': 32
    },
    'tvnet': {
        'resolver': '/resources/lib/channels/tr/tvnet:get_live_url',
        'label': 'Tvnet',
        'thumb': 'channels/tr/tvnet.jpg',
        'fanart': 'channels/tr/tvnet_fanart.jpg',
        'enabled': True,
        'order': 33
    },
    'ulke': {
        'resolver': '/resources/lib/channels/tr/ulke:get_live_url',
        'label': 'Ulke TV',
        'thumb': 'channels/tr/ulke.png',
        'fanart': 'channels/tr/ulke_fanart.jpg',
        'enabled': True,
        'order': 34
    },
    'vavtv': {
        'resolver': '/resources/lib/channels/tr/atv:get_live_url',
        'label': 'Vav TV',
        'thumb': 'channels/tr/vav.png',
        'fanart': 'channels/tr/vav_fanart.jpg',
        'enabled': True,
        'order': 35
    },
}
