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


CATEGORIES = {
    'main_menu.be': 'Belgian channels',
    'main_menu.ca': 'Canadian channels',
    'main_menu.fr': 'French channels',
    'main_menu.jp': 'Japanese channels',
    'main_menu.sw': 'Switzerland channels',
    'main_menu.uk': 'United Kingdom channels',
    'main_menu.wo': 'International channels',
    'main_menu.ws': 'Websites'
}

CHANNELS = {

    'main_menu.be': {
        'channels.be.rtbf.auvio': 'RTBF Auvio (La Une, La deux, La Trois, ...)',
        'channels.be.bvn.bvn': 'BVN',
        'channels.be.brf.brf': 'BRF Mediathek',
        'channels.be.rtl.rtltvi': 'RTL-TVI',
        'channels.be.rtl.plugrtl': 'PLUG RTL',
        'channels.be.rtl.clubrtl': 'CLUB RTL',
        'channels.be.vrt.vrt': 'VRT NU'
    },

    'main_menu.ca': {
        'channels.ca.tv5.tv5': 'TV5',
        'channels.ca.tv5.unis': 'UNIS'
    },

    'main_menu.sw': {
        'channels.sw.srgssr.rts': 'RTS',
        'channels.sw.srgssr.rsi': 'RSI',
        'channels.sw.srgssr.srf': 'SRF',
        'channels.sw.srgssr.rtr': 'RTR',
        'channels.sw.srgssr.swissinfo': 'SWISSINFO',
        'channels.sw.rougetv.rougetv': 'Rouge TV'
    },

    'main_menu.fr': {
        'channels.fr.tf1.tf1': 'TF1',
        'channels.fr.pluzz.france2': 'France 2',
        'channels.fr.pluzz.france3': 'France 3',
        'channels.fr.mycanal.canalplus': 'Canal +',
        'channels.fr.pluzz.france5': 'France 5',
        'channels.fr.6play.m6': 'M6',
        'channels.fr.mycanal.c8': 'C8',
        'channels.fr.6play.w9': 'W9',
        'channels.fr.tf1.tmc': 'TMC',
        'channels.fr.tf1.nt1': 'NT1',
        'channels.fr.nrj.nrj12': 'NRJ 12',
        'channels.fr.pluzz.france4': 'France 4',
        'channels.fr.bfmtv.bfmtv': 'BFM TV',
        'channels.fr.cnews.cnews': 'CNews',
        'channels.fr.mycanal.cstar': 'CStar',
        'channels.fr.gulli.gulli': 'Gulli',
        'channels.fr.pluzz.franceo': 'France Ô',
        'channels.fr.tf1.hd1': 'HD1',
        'channels.fr.lequipe.lequipe': 'L\'Équipe',
        'channels.fr.6play.6ter': '6ter',
        'channels.fr.numero23.numero23': 'Numéro 23',
        'channels.fr.nrj.cherie25': 'Chérie 25',
        'channels.fr.pluzz.la_1ere': 'La 1ère (Outre-Mer)',
        'channels.fr.pluzz.franceinfo': 'France Info',
        'channels.fr.bfmtv.bfmbusiness': 'BFM Business',
        'channels.fr.bfmtv.rmc': 'RMC',
        'channels.fr.bfmtv.01net': '01Net TV',
        'channels.fr.tf1.tfou': 'Tfou (MYTF1)',
        'channels.fr.tf1.xtra': 'Xtra (MYTF1)',
        'channels.fr.tf1.lci': 'LCI',
        'channels.fr.lcp.lcp': 'LCP Assemblée Nationale',
        'channels.fr.bfmtv.rmcdecouverte': 'RMC Découverte HD24',
        'channels.fr.6play.stories': 'Stories (6play)',
        'channels.fr.6play.bruce': 'Bruce (6play)',
        'channels.fr.6play.crazy_kitchen': 'Crazy Kitchen (6play)',
        'channels.fr.6play.home': 'Home Time (6play)',
        'channels.fr.6play.styles': 'Sixième Style (6play)',
        'channels.fr.6play.comedy': 'Comic (6play)',
        'channels.fr.publicsenat.publicsenat': 'Public Sénat',
        'channels.fr.pluzz.france3regions': 'France 3 Régions',
        'channels.fr.pluzz.francetvsport': 'France TV Sport (francetv)',
        'channels.fr.tf1thematiques.histoire': 'Histoire',
        'channels.fr.tf1thematiques.tvbreizh': 'TV Breizh',
        'channels.fr.tf1thematiques.ushuaiatv': 'Ushuaïa TV',
        'channels.fr.pluzz.studio-4': 'Studio 4 (francetv)',
        'channels.fr.pluzz.irl': 'IRL (francetv)',
        'channels.fr.mycanal.seasons': 'Seasons',
        'channels.fr.mycanal.comedie': 'Comédie +',
        'channels.fr.mycanal.les-chaines-planete': 'Les chaînes planètes +',
        'channels.fr.mycanal.golfplus': 'Golf +',
        'channels.fr.mycanal.cineplus': 'Ciné +',
        'channels.fr.mycanal.infosportplus': 'INFOSPORT+'
    },

    'main_menu.jp': {
        'channels.jp.nhk.nhknews': 'NHK ニュース',
        'channels.jp.nhk.nhklifestyle': 'NHKらいふ',
        'channels.jp.tbs.tbsnews': 'TBS ニュース'
    },

    'main_menu.uk': {
        'channels.uk.blaze.blaze': 'Blaze',
        'channels.uk.uktvplay.dave': 'Dave',
        'channels.uk.uktvplay.really': 'Really',
        'channels.uk.uktvplay.yesterday': 'Yesterday',
        'channels.uk.uktvplay.drama': 'Drama',
        'channels.uk.sky.skynews': 'Sky News',
        'channels.uk.sky.skysports': 'Sky sports'
    },

    'main_menu.wo': {
        'channels.wo.tv5monde.tv5mondeafrique': 'TV5Monde Afrique',
        'channels.wo.arte.arte': 'Arte',
        'channels.wo.euronews.euronews': 'Euronews',
        'channels.wo.france24.france24': 'France 24',
        'channels.wo.nhkworld.nhkworld': 'NHK World',
        'channels.wo.tv5monde.tv5monde': 'TV5Monde',
        'channels.wo.tv5monde.tivi5monde': 'Tivi 5Monde'
    },

    'main_menu.ws': {
        'channels.ws.allocine.allocine': 'Allociné',
        'channels.ws.tetesaclaques.tetesaclaques': 'Au pays des Têtes à claques',
        'channels.ws.taratata.taratata': 'Taratata',
        'channels.ws.noob.noob': 'Noob TV',
        'channels.ws.culturepub.culturepub': 'Culturepub',
        'channels.ws.autoplus.autoplus': 'Auto Plus',
        'channels.ws.notrehistoirech.notrehistoirech': 'Notre Histoire.ch',
        'channels.ws.30millionsdamis.30millionsdamis': '30 Millions d\'Amis'
    }
}
