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


# SKELETON dictionary corresponds to the different level of menus of the addon
# (elt1, elt2) --> elt1: level label, elt2: next function to call

SKELETON = {
    ('root', 'root'): {

        ('live_tv', 'root'): {

            ('fr', 'build_live_tv_menu'): {

                'tf1.tf1',
                'pluzz.france2',
                'pluzz.france3'
            },

            ('be', 'build_live_tv_menu'): {
                'rtbf.auvio',
                'bvn.bvn',
                'brf.brf',
                'rtl.rtltvi',
                'rtl.plugrtl',
                'rtl.clubrtl'
            }
        },

        ('replay', 'root'): {

            ('be', 'root'): {
                ('auvio', 'replay_entry'),
                ('bvn', 'replay_entry'),
                ('brf', 'replay_entry'),
                ('rtltvi', 'replay_entry'),
                ('plugrtl', 'replay_entry'),
                ('clubrtl' 'replay_entry')
            },

            ('fr', 'root'): {
                ('tf1', 'replay_entry'),
                ('france2', 'replay_entry'),
                ('france3', 'replay_entry'),
                ('cplus', 'replay_entry'),
                ('france5', 'replay_entry'),
                ('m6', 'replay_entry')
            }
        }
    }
}


# FOLDERS dict corresponds to the folder to use for the label in SKELETON
# If folder if the same as SKELETON label it's optionnal
FOLDERS = {
    'live_tv': 'channels',
    'replay': 'channels'
}


CHANNELS = {
    'tf1': 'tf1',
    'france2': 'pluzz'
}


# LABELS dict is only used to retrieve string to display on Kodi
LABELS = {

    # root
    'live_tv': 'Live TV',
    'replay': 'Catch-up TV',
    'websites': 'Websites',

    # Countries
    'be': 'Belgium',
    'fr': 'France',
    'jp': 'Japan',
    'ch': 'Switzerland',
    'gb': 'United Kingdom',
    'wo': 'International',

    # Belgium channels / live TV
    'rtbf.auvio': 'RTBF Auvio (La Une, La deux, La Trois, ...)',
    'bvn.bvn': 'BVN',
    'brf.brf': 'BRF Mediathek',
    'rtl.rtltvi': 'RTL-TVI',
    'rtl.plugrtl': 'PLUG RTL',
    'rtl.clubrtl': 'CLUB RTL',

    # French channels / live TV
    'tf1': 'TF1',
    'france2': 'France 2',
    'france3': 'France 3',
    'groupecanal.cplus': 'Canal +',
    'pluzz.france5': 'France 5',
    '6play.m6': 'M6',
    'groupecanal.c8': 'C8',
    '6play.w9': 'W9',
    'tf1.tmc': 'TMC',
    'tf1.nt1': 'NT1',
    'nrj.nrj12': 'NRJ 12',
    'pluzz.france4': 'France 4',
    'bfmtv.bfmtv': 'BFM TV',
    'groupecanal.cnews': 'CNews',
    'groupecanal.cstar': 'CStar',
    'gulli.gulli': 'Gulli',
    'pluzz.franceo': 'France Ô',
    'tf1.hd1': 'HD1',
    'lequipe.lequipe': 'L\'Équipe',
    '6play.6ter': '6ter',
    'numero23.numero23': 'Numéro 23',
    'nrj.cherie25': 'Chérie 25',
    'pluzz.la_1ere': 'La 1ère (Outre-Mer)',
    'pluzz.franceinfo': 'France Info',
    'bfmtv.bfmbusiness': 'BFM Business',
    'bfmtv.rmc': 'RMC',
    'bfmtv.01net': '01Net TV',
    'tf1.tfou': 'Tfou (MYTF1)',
    'tf1.xtra': 'Xtra (MYTF1)',
    'tf1.lci': 'LCI',
    'lcp.lcp': 'LCP Assemblée Nationale',
    'bfmtv.rmcdecouverte': 'RMC Découverte HD24',
    '6play.stories': 'Stories (6play)',
    '6play.bruce': 'Bruce (6play)',
    '6play.crazy_kitchen': 'Crazy Kitchen (6play)',
    '6play.home': 'Home Time (6play)',
    '6play.styles': 'Sixième Style (6play)',
    '6play.comedy': 'Comic (6play)',
    'publicsenat.publicsenat': 'Public Sénat',
    'pluzz.france3regions': 'France 3 Régions',
    'pluzz.francetvsport': 'France TV Sport (francetv)',

    # Japan channels / live TV
    'nhk.nhknews': 'NHK ニュース',
    'nhk.nhklifestyle': 'NHKらいふ',
    'tbs.tbsnews': 'TBS ニュース',

    # Switzerland channels / live TV
    'srgssr.rts': 'RTS',
    'srgssr.rsi': 'RSI',
    'srgssr.srf': 'SRF',
    'srgssr.rtr': 'RTR',
    'srgssr.swissinfo': 'SWISSINFO',

    # United Kingdom channels / live TV
    'blaze.blaze': 'Blaze',
    'uktvplay.dave': 'Dave',
    'uktvplay.really': 'Really',
    'uktvplay.yesterday': 'Yesterday',
    'uktvplay.drama': 'Drama',

    # International channels / live TV
    'tv5monde.tv5mondeafrique': 'TV5Monde Afrique',
    'arte.arte': 'Arte',
    'euronews.euronews': 'Euronews',
    'france24.france24': 'France 24',
    'nhkworld.nhkworld': 'NHK World',
    'tv5monde.tv5monde': 'TV5Monde',
    'tv5monde.tivi5monde': 'Tivi 5Monde',

    # Websites
    'allocine': 'Allociné',
    'tetesaclaques': 'Au pays des Têtes à claques',
    'taratata': 'Taratata',
    'noob': 'Noob TV',
    'culturepub': 'Culturepub'


}
