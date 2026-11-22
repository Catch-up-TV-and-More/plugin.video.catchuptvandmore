# -*- coding: utf-8 -*-
# Copyright: (c) 2016, SylvainCecchetto
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
    'tvp1': {
        'resolver': '/resources/lib/channels/pl/tvp:get_live_url',
        'label': 'TVP 1',
        'thumb': 'channels/pl/tvp1.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVP1.pl',
        'epg_id': 399697,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 1
    },
    'tvp2': {
        'resolver': '/resources/lib/channels/pl/tvp:get_live_url',
        'label': 'TVP 2',
        'thumb': 'channels/pl/tvp2.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVP2.pl',
        'epg_id': 399698,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 2
    },
    'tvp3': {
        'resolver': '/resources/lib/channels/pl/tvp:get_live_url',
        'label': 'TVP 3',
        'thumb': 'channels/pl/tvp3.png',
        'fanart': 'channels/pl/tvp.png',
        'available_languages': {
            "Białystok": {'xmltv_id': 'TVP3Bialystok.pl', 'epg_id': 399732},
            "Bydgoszcz": {'xmltv_id': 'TVP3Bydgoszcz.pl', 'epg_id': 399740},
            "Gdańsk": {'xmltv_id': 'TVP3Gdansk.pl', 'epg_id': 399741},
            "Gorzów Wielkopolski": {'xmltv_id': 'TVP3GorzowWielkopolski.pl', 'epg_id': 399742},
            "Katowice": {'xmltv_id': 'TVP3Katowice.pl', 'epg_id': 399743},
            "Kielce": {'xmltv_id': 'TVP3Kielce.pl', 'epg_id': 399745},
            "Kraków": {'xmltv_id': 'TVP3Krakow.pl', 'epg_id': 399746},
            "Lublin": {'xmltv_id': 'TVP3Lublin.pl', 'epg_id': 399748},
            "Łódź": {'xmltv_id': 'TVP3Lodz.pl', 'epg_id': 399747},
            "Olsztyn": {'xmltv_id': 'TVP3Olsztyn.pl', 'epg_id': 399749},
            "Opole": {'xmltv_id': 'TVP3Opole.pl', 'epg_id': 399750},
            "Poznań": {'xmltv_id': 'TVP3Poznan.pl', 'epg_id': 399751},
            "Rzeszów": {'xmltv_id': 'TVP3Rzeszow.pl', 'epg_id': 399752},
            "Szczecin": {'xmltv_id': 'TVP3Szczecin.pl', 'epg_id': 399753},
            "Warszawa": {'xmltv_id': 'TVP3Warszawa.pl', 'epg_id': 399754},
            "Wrocław": {'xmltv_id': 'TVP3Wroclaw.pl', 'epg_id': 399755},
        },
        'epg_source': 'tvp',
        'enabled': True,
        'order': 3
    },
    'tvpinfo': {
        'resolver': '/resources/lib/channels/pl/tvp:get_live_url',
        'label': 'TVP Info',
        'thumb': 'channels/pl/tvpinfo.png',
        'fanart': 'channels/pl/tvpinfo_fanart.png',
        'xmltv_id': 'TVPInfo.pl',
        'epg_id': 399699,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 4
    },
    'tvpworld': {
        'resolver': '/resources/lib/channels/pl/tvp:get_live_url',
        'label': 'TVP World',
        'thumb': 'channels/pl/tvpworld.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPWorld.pl',
        'epg_id': 399731,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 5
    },
    'tvppolonia': {
        'resolver': '/resources/lib/channels/pl/tvp:get_live_url',
        'label': 'TVP Polonia',
        'thumb': 'channels/pl/tvppolonia.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPPolonia.pl',
        'epg_id': 399723,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 6
    },
    'tvpwilno': {
        'resolver': '/resources/lib/channels/pl/tvp:get_live_url',
        'label': 'TVP Wilno',
        'thumb': 'channels/pl/tvpwilno.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPWilno.pl',
        'epg_id': 999687,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 7
    },
    'tvpalfa': {
        'resolver': '/resources/lib/channels/pl/tvp:get_live_url',
        'label': 'TVP Alfa',
        'thumb': 'channels/pl/tvpalfa.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'AlfaTVP.pl',
        'epg_id': 399726,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 8
    },
    'tvpabc': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP ABC',
        'thumb': 'channels/pl/tvpabc.png',
        'fanart': 'channels/pl/tvpabc_fanart.jpg',
        'xmltv_id': 'TVPABC.pl',
        'epg_id': 399704,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 10
    },
    'tvpabc2': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP ABC 2',
        'thumb': 'channels/pl/tvpabc2.png',
        'fanart': 'channels/pl/tvpabc_fanart.jpg',
        'xmltv_id': 'TVPABC2.pl',
        'epg_id': 399727,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 11
    },
    'tvpkryminaly': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP Kryminały',
        'thumb': 'channels/pl/tvpkryminaly.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPKryminaly.pl',
        'epg_id': 2543050,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 15
    },
    'tvpmilosc': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP Miłość',
        'thumb': 'channels/pl/tvpmilosc.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPMilosc.pl',
        'epg_id': 2724087,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 16
    },
    'tvpmuzyka': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP Muzyka i Koncerty',
        'thumb': 'channels/pl/tvpmuzyka.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPMuzykaiKoncerty.pl',
        'epg_id': 2999109,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 17
    },
    'tvpkultura': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP Kultura',
        'thumb': 'channels/pl/tvpkultura.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPKultura.pl',
        'epg_id': 399700,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 18
    },
    'tvpkobieta': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP Kobieta',
        'thumb': 'channels/pl/tvpkobieta.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPKobieta.pl',
        'epg_id': 399701,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 19
    },
    'tvpsport': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP Sport',
        'thumb': 'channels/pl/tvpsport.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPSport.pl',
        'epg_id': 399702,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 20
    },
    'tvphistoria': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP Historia',
        'thumb': 'channels/pl/tvphistoria.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPHistoria.pl',
        'epg_id': 399703,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 21
    },
    'tvpdokument': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP Dokument',
        'thumb': 'channels/pl/tvpdokument.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPDokument.pl',
        'epg_id': 399721,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 22
    },
    'tvpnauka': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP Nauka',
        'thumb': 'channels/pl/tvpnauka.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPNauka.pl',
        'epg_id': 399722,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 23
    },
    'tvprozrywka': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP Rozrywka',
        'thumb': 'channels/pl/tvprozrywka.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPRozrywka.pl',
        'epg_id': 399724,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 24
    },
    'tvphistoria2': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP Historia 2',
        'thumb': 'channels/pl/tvphistoria2.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPHistoria2.pl',
        'epg_id': 399725,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 25
    },
    'tvpkultura2': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP Kultura 2',
        'thumb': 'channels/pl/tvpkultura2.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPKultura2.pl',
        'epg_id': 399728,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 26
    },
    'belsat': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'Belsat',
        'thumb': 'channels/pl/belsat.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'BelsatTV.pl',
        'epg_id': 399729,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 27
    },
    'tvpsejm': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP Parlament Sejm',
        'thumb': 'channels/pl/tvpsejm.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPParlamentSejm.pl',
        'epg_id': 1065594,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 28
    },
    'tvpsenat': {
        'resolver': '/resources/lib/channels/pl/tvp:get_vod_live_url',
        'label': 'TVP Parlament Senat',
        'thumb': 'channels/pl/tvpsenat.png',
        'fanart': 'channels/pl/tvp.png',
        'xmltv_id': 'TVPParlamentSenat.pl',
        'epg_id': 1065595,
        'epg_source': 'tvp',
        'enabled': True,
        'order': 29
    },
}
