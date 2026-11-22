# -*- coding: utf-8 -*-
# Copyright: (c) 2016, SylvainCecchetto
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
    'blaze': {
        'resolver': '/resources/lib/channels/uk/blaze:get_live_url',
        'label': 'Blaze',
        'thumb': 'channels/uk/blaze.png',
        'fanart': 'channels/uk/blaze_fanart.jpg',
        'xmltv_id': '64.freeview.co.uk',
        'enabled': True,
        'order': 1
    },
    'dave': {
        'resolver': '/resources/lib/channels/uk/uktvplay:get_live_url',
        'label': 'U&Dave',
        'thumb': 'channels/uk/dave.png',
        'fanart': 'channels/uk/dave_fanart.jpg',
        'xmltv_id': '19.freeview.co.uk',
        'enabled': False,
        'order': 2
    },
    'yesterday': {
        'resolver': '/resources/lib/channels/uk/uktvplay:get_live_url',
        'label': 'U&Yesterday',
        'thumb': 'channels/uk/yesterday.png',
        'fanart': 'channels/uk/yesterday_fanart.jpg',
        'xmltv_id': '27.freeview.co.uk',
        'enabled': False,
        'order': 3
    },
    'drama': {
        'resolver': '/resources/lib/channels/uk/uktvplay:get_live_url',
        'label': 'U&Drama',
        'thumb': 'channels/uk/drama.png',
        'fanart': 'channels/uk/drama_fanart.jpg',
        'xmltv_id': '20.freeview.co.uk',
        'enabled': False,
        'order': 4
    },
    'skynews': {
        'resolver': '/resources/lib/channels/uk/sky:get_live_url',
        'label': 'Sky News',
        'thumb': 'channels/uk/skynews.png',
        'fanart': 'channels/uk/skynews_fanart.jpg',
        'xmltv_id': '233.freeview.co.uk',
        'enabled': True,
        'order': 5
    },
    'stv': {
        'resolver': '/resources/lib/channels/uk/stv:get_live_url',
        'label': 'STV',
        'thumb': 'channels/uk/stv.png',
        'fanart': 'channels/uk/stv_fanart.jpg',
        'xmltv_id': '103.freeview.co.uk',
        'enabled': True,
        'order': 6
    },
    'stv-plus-1': {
        'resolver': '/resources/lib/channels/uk/stv:get_live_url',
        'label': 'STV +1',
        'thumb': 'channels/uk/stv_plusone.png',
        'xmltv_id': '35.freeview.co.uk',
        'enabled': True,
        'order': 7
    },
    'C4': {
        'resolver': '/resources/lib/channels/uk/channel4:get_live_url',
        'label': 'Channel 4',
        'thumb': 'channels/uk/channel4_tv.png',
        'fanart': 'channels/uk/channel4_tv_fanart.jpg',
        'xmltv_id': '4.freeview.co.uk',
        'enabled': True,
        'order': 8
    },
    'E4': {
        'resolver': '/resources/lib/channels/uk/channel4:get_live_url',
        'label': 'E4',
        'thumb': 'channels/uk/E4.png',
        'fanart': 'channels/uk/E4_fanart.jpg',
        'xmltv_id': '13.freeview.co.uk',
        'enabled': True,
        'order': 9
    },
    'M4': {
        'resolver': '/resources/lib/channels/uk/channel4:get_live_url',
        'label': 'More4',
        'thumb': 'channels/uk/More4.png',
        'fanart': 'channels/uk/More4_fanart.jpg',
        'xmltv_id': '18.freeview.co.uk',
        'enabled': True,
        'order': 10
    },
    'F4': {
        'resolver': '/resources/lib/channels/uk/channel4:get_live_url',
        'label': 'Film4',
        'thumb': 'channels/uk/Film4.png',
        'fanart': 'channels/uk/Film4_fanart.jpg',
        'xmltv_id': '14.freeview.co.uk',
        'enabled': True,
        'order': 11
    },
    '4S': {
        'resolver': '/resources/lib/channels/uk/channel4:get_live_url',
        'label': '4seven',
        'thumb': 'channels/uk/4seven.png',
        'fanart': 'channels/uk/4seven_fanart.jpg',
        'xmltv_id': '49.freeview.co.uk',
        'enabled': True,
        'order': 12
    },
    'birminghamlocal': {
        'resolver': '/resources/lib/channels/uk/uklocaltv:get_live_url',
        'label': 'Birmingham Local TV',
        'thumb': 'channels/uk/birminghamlocal.png',
        'fanart': 'channels/uk/birminghamlocal_fanart.jpg',
        'enabled': False,
        'order': 13
    },
    'bristollocal': {
        'resolver': '/resources/lib/channels/uk/uklocaltv:get_live_url',
        'label': 'Bristol Local TV',
        'thumb': 'channels/uk/bristollocal.png',
        'fanart': 'channels/uk/bristollocal_fanart.jpg',
        'enabled': False,
        'order': 14
    },
    'cardifflocal': {
        'resolver': '/resources/lib/channels/uk/uklocaltv:get_live_url',
        'label': 'Cardiff Local TV',
        'thumb': 'channels/uk/cardifflocal.png',
        'fanart': 'channels/uk/cardifflocal_fanart.jpg',
        'enabled': False,
        'order': 15
    },
    'leedslocal': {
        'resolver': '/resources/lib/channels/uk/uklocaltv:get_live_url',
        'label': 'Leeds Local TV',
        'thumb': 'channels/uk/leedslocal.png',
        'fanart': 'channels/uk/leedslocal_fanart.jpg',
        'enabled': False,
        'order': 16
    },
    'liverpoollocal': {
        'resolver': '/resources/lib/channels/uk/uklocaltv:get_live_url',
        'label': 'Liverpool Local TV',
        'thumb': 'channels/uk/liverpoollocal.png',
        'fanart': 'channels/uk/liverpoollocal_fanart.jpg',
        'enabled': False,
        'order': 17
    },
    'northwaleslocal': {
        'resolver': '/resources/lib/channels/uk/uklocaltv:get_live_url',
        'label': 'North Wales Local TV',
        'thumb': 'channels/uk/northwaleslocal.png',
        'fanart': 'channels/uk/northwaleslocal_fanart.jpg',
        'enabled': False,
        'order': 18
    },
    'teessidelocal': {
        'resolver': '/resources/lib/channels/uk/uklocaltv:get_live_url',
        'label': 'Teesside Local TV',
        'thumb': 'channels/uk/teessidelocal.png',
        'fanart': 'channels/uk/teessidelocal_fanart.jpg',
        'enabled': False,
        'order': 19
    },
    'twlocal': {
        'resolver': '/resources/lib/channels/uk/uklocaltv:get_live_url',
        'label': 'Tyne & Wear Local TV',
        'thumb': 'channels/uk/twlocal.png',
        'fanart': 'channels/uk/twlocal_fanart.jpg',
        'enabled': False,
        'order': 20
    },
    'really': {
        'resolver': '/resources/lib/channels/uk/discoveryplus:get_live_url',
        'label': 'Really',
        'thumb': 'channels/uk/really.png',
        'fanart': 'channels/uk/really_fanart.jpg',
        'xmltv_id': '17.freeview.co.uk',
        'enabled': False,
        'order': 21
    },
    'food-network': {
        'resolver': '/resources/lib/channels/uk/discoveryplus:get_live_url',
        'label': 'Food Network',
        'thumb': 'channels/uk/foodnetwork.png',
        'fanart': 'channels/uk/foodnetwork_fanart.jpg',
        'xmltv_id': '43.freeview.co.uk',
        'enabled': False,
        'order': 22
    },
    'dmax': {
        'resolver': '/resources/lib/channels/uk/discoveryplus:get_live_url',
        'label': 'DMAX',
        'thumb': 'channels/uk/dmax.png',
        'fanart': 'channels/uk/dmax_fanart.jpg',
        'xmltv_id': '39.freeview.co.uk',
        'enabled': False,
        'order': 23
    },
    'home': {
        'resolver': '/resources/lib/channels/uk/discoveryplus:get_live_url',
        'label': 'HGTV',
        'thumb': 'channels/uk/hgtv.png',
        'fanart': 'channels/uk/hgtv_fanart.jpg',
        'xmltv_id': '44.freeview.co.uk',
        'enabled': False,
        'order': 24
    },
    'quest': {
        'resolver': '/resources/lib/channels/uk/discoveryplus:get_live_url',
        'label': 'Quest',
        'thumb': 'channels/uk/questtv.png',
        'fanart': 'channels/uk/questtv_fanart.jpg',
        'xmltv_id': '12.freeview.co.uk',
        'enabled': False,
        'order': 25
    },
    'quest-red': {
        'resolver': '/resources/lib/channels/uk/discoveryplus:get_live_url',
        'label': 'Quest RED',
        'thumb': 'channels/uk/questred.png',
        'fanart': 'channels/uk/questred_fanart.jpg',
        'xmltv_id': '40.freeview.co.uk',
        'enabled': False,
        'order': 26
    },
    'C5': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5',
        'thumb': 'channels/uk/five.png',
        'fanart': 'channels/uk/five_fanart.jpg',
        'xmltv_id': '5.freeview.co.uk',
        'enabled': True,
        'order': 27
    },
    'C6': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 Star',
        'thumb': 'channels/uk/fivestar.png',
        'fanart': 'channels/uk/fivestar_fanart.jpg',
        'xmltv_id': '32.freeview.co.uk',
        'enabled': True,
        'order': 28
    },
    'C7': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 USA',
        'thumb': 'channels/uk/fiveusa.png',
        'fanart': 'channels/uk/fiveusa_fanart.jpg',
        'xmltv_id': '21.freeview.co.uk',
        'enabled': True,
        'order': 29
    },
    'C0': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 Action',
        'thumb': 'channels/uk/5action.png',
        'fanart': 'channels/uk/5action_fanart.jpg',
        'xmltv_id': '46.freeview.co.uk',
        'enabled': True,
        'order': 30
    },
    'C8': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 Drama',
        'thumb': 'channels/uk/5select.png',
        'fanart': 'channels/uk/5select_fanart.jpg',
        'xmltv_id': '33.freeview.co.uk',
        'enabled': True,
        'order': 31
    },
    'C5CH02': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 Police Interceptors',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/C5CH02/512x512.png',
        'xmltv_id': 'C5CH02',
        'epg_source': 'my5',
        'enabled': True,
        'order': 32
    },
    'C5CH01': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 Cops',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/C5CH01/512x512.png',
        'xmltv_id': 'C5CH01',
        'epg_source': 'my5',
        'enabled': True,
        'order': 33
    },
    'C5CH18': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 Christmas In Summer',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/C5CH18/512x512.png',
        'xmltv_id': 'C5CH18',
        'epg_source': 'my5',
        'enabled': True,
        'order': 34
    },
    'C5CH16': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 Movies',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/C5CH16/512x512.png',
        'xmltv_id': 'C5CH16',
        'epg_source': 'my5',
        'enabled': True,
        'order': 35
    },
    'C5CH05': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 Bargain-Loving Brits',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/C5CH05/512x512.png',
        'xmltv_id': 'C5CH05',
        'epg_source': 'my5',
        'enabled': True,
        'order': 36
    },
    'C5CH07': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 A&E',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/C5CH07/512x512.png',
        'xmltv_id': 'C5CH07',
        'epg_source': 'my5',
        'enabled': True,
        'order': 37
    },
    'C5CH10': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 Crime',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/C5CH10/512x512.png',
        'xmltv_id': 'C5CH10',
        'epg_source': 'my5',
        'enabled': True,
        'order': 38
    },
    'C5CH04': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 Medical',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/C5CH04/512x512.png',
        'xmltv_id': 'C5CH04',
        'epg_source': 'my5',
        'enabled': True,
        'order': 39
    },
    'C5CH03': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 Trucking Hell',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/C5CH03/512x512.png',
        'xmltv_id': 'C5CH03',
        'epg_source': 'my5',
        'enabled': True,
        'order': 40
    },
    'C5CH06': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 Yorkshire Vet',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/C5CH06/512x512.png',
        'xmltv_id': 'C5CH06',
        'epg_source': 'my5',
        'enabled': True,
        'order': 41
    },
    'C5CH09': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': '5 History',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/C5CH09/512x512.png',
        'xmltv_id': 'C5CH09',
        'epg_source': 'my5',
        'enabled': True,
        'order': 42
    },
    'C5CH14': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': 'MTV Reality',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/C5CH14/512x512.png',
        'xmltv_id': 'C5CH14',
        'epg_source': 'my5',
        'enabled': True,
        'order': 43
    },
    'C5CH11': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': 'Milkshake!',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/C5CH11/512x512.png',
        'xmltv_id': 'C5CH11',
        'epg_source': 'my5',
        'enabled': True,
        'order': 44
    },
    '3P-HEARST-FAST-01': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': 'Inside Crime',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/3P-HEARST-FAST-01/512x512.png',
        'xmltv_id': '3P-HEARST-FAST-01',
        'epg_source': 'my5',
        'enabled': True,
        'order': 45
    },
    '3P-HEARST-FAST-02': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': 'Mystery TV',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/3P-HEARST-FAST-02/512x512.png',
        'xmltv_id': '3P-HEARST-FAST-02',
        'epg_source': 'my5',
        'enabled': True,
        'order': 46
    },
    '3P-AMC-FAST-03': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': 'True Crime UK',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/3P-AMC-FAST-03/512x512.png',
        'xmltv_id': '3P-AMC-FAST-03',
        'epg_source': 'my5',
        'enabled': True,
        'order': 47
    },
    '3P-AMC-FAST-04': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': 'Love After Lockup',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/3P-AMC-FAST-04/512x512.png',
        'xmltv_id': '3P-AMC-FAST-04',
        'epg_source': 'my5',
        'enabled': True,
        'order': 48
    },
    '3P-AMC-FAST-01': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': 'AMC Reality',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/3P-AMC-FAST-01/512x512.png',
        'xmltv_id': '3P-AMC-FAST-01',
        'epg_source': 'my5',
        'enabled': True,
        'order': 49
    },
    '3P-AMC-FAST-02': {
        'resolver': '/resources/lib/channels/uk/my5:get_live_url',
        'label': 'AMC Cupid',
        'thumb': 'https://api-images.channel5.com/otis/images/channel/3P-AMC-FAST-02/512x512.png',
        'xmltv_id': '3P-AMC-FAST-02',
        'epg_source': 'my5',
        'enabled': True,
        'order': 50
    },
    'great-romance': {
        'resolver': '/resources/lib/channels/uk/stv:get_live_url',
        'label': 'Great! Christmas',
        'thumb': 'https://player.api.stv.tv/v1/images/975027/rendition/?redirect=true&width=512&height=512',
        'xmltv_id': 'great-romance',
        'epg_source': 'stv',
        'enabled': True,
        'order': 51
    },
    'great-mystery': {
        'resolver': '/resources/lib/channels/uk/stv:get_live_url',
        'label': 'Great! Mystery',
        'thumb': 'https://player.api.stv.tv/v1/images/906988/rendition/?redirect=true&width=512&height=512',
        'xmltv_id': 'great-mystery',
        'epg_source': 'stv',
        'enabled': True,
        'order': 52
    },
    'great-movies': {
        'resolver': '/resources/lib/channels/uk/stv:get_live_url',
        'label': 'Great! Movies',
        'thumb': 'https://player.api.stv.tv/v1/images/906994/rendition/?redirect=true&width=512&height=512',
        'xmltv_id': 'great-movies',
        'epg_source': 'stv',
        'enabled': True,
        'order': 53
    },
}
