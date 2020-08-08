#!/usr/bin/env python3
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
from __future__ import print_function

import importlib
import os
from builtins import str
import polib
import sys
import mock
import urllib.parse

PLUGIN_PATH = os.path.dirname(os.path.abspath(__file__)) + '/../plugin.video.catchuptvandmore'

sys.path.append(PLUGIN_PATH)
sys.path.append(PLUGIN_PATH + '/resources')
sys.path.append(PLUGIN_PATH + '/resources/lib')

sys.modules['codequick'] = mock.MagicMock()

LIVE_TV_M3U_ALL_FILEPATH = PLUGIN_PATH + "/resources/m3u/live_tv_all.m3u"

LIVE_TV_M3U_COUTRY_FILEPATH = PLUGIN_PATH + "/resources/m3u/live_tv_%s.m3u"
# arg0: country_code (fr, nl, jp, ...)

EN_STRINGS_PO_FILEPATH = PLUGIN_PATH + "/resources/language/resource.language.en_gb/strings.po"

PLUGIN_KODI_PATH = "plugin://plugin.video.catchuptvandmore"

M3U_ENTRY = '#EXTINF:-1 tvg-id="%s" tvg-logo="%s" group-title="%s",%s\n%s'
# arg0: tgv_id
# arg1: tgv_logo
# arg2: group_title
# arg3: label
# arg4: URL

# Parse english strings.po
# in order to recover labels
# Key format: "#30500"
# Value format: "France"
en_strings_po = {}
po = polib.pofile(EN_STRINGS_PO_FILEPATH)
for entry in po:
    en_strings_po[entry.msgctxt] = entry.msgid

MANUAL_LABELS = {
    'la_1ere': 'La 1ère',
    'france3regions': 'France 3 Régions',
    'euronews': 'Euronews',
    'arte': 'Arte',
    'dw': 'DW',
    'france24': 'France 24',
    'qvc': 'QVC',
    'nhkworld': 'NHK World',
    'cgtn': 'CGTN',
    'paramountchannel': 'Paramount Channel',
    'rt': 'RT',
    'tvp3': 'TVP 3',
    'realmadridtv': 'Realmadrid TV',
    'icitele': 'ICI Télé',
    'cbc': 'CBC'
}


def get_item_media_path(item_media_path):
    """Get full path or URL of an item_media

    Args:
        item_media_path (str or list): Partial media path of the item (e.g. channels/fr/tf1.png)
    Returns:
        str: Full path or URL of the item_pedia
    """
    full_path = ''

    # Remote image with complete URL
    if 'http' in item_media_path:
        full_path = item_media_path

    # Image in our resource.images add-on
    else:
        full_path = 'resource://resource.images.catchuptvandmore/' + item_media_path

    return full_path


# Return string label from item_id
def get_label(item_id, item_infos={}):
    if 'label' in item_infos:
        label = item_infos['label']
    else:
        label = item_id

    # strings.po case
    if isinstance(label, int):
        if ('#' + str(label)) in en_strings_po:
            return en_strings_po['#' + str(label)]
        else:
            print('Number ' + str(label) + ' not found in english strings.po')
            exit(-1)

    # manual label case
    elif item_id in MANUAL_LABELS:
        return MANUAL_LABELS[item_id]

    return label


# Write M3U header in file
def write_header(file):
    file.write("#EXTM3U tvg-shift=0\n\n")


# Generate m3u files
def generate_m3u_files():

    countries_m3u = {}

    # Iterate over countries
    live_tv = importlib.import_module('lib.skeletons.live_tv').menu
    for country_id, country_infos in list(live_tv.items()):

        # fr_live
        print('\n# country_id: ' + country_id)

        # France
        country_label = get_label(country_id, country_infos)

        # fr
        country_code = country_id.replace('_live', '')

        countries_m3u[country_id] = {}
        countries_m3u[country_id]['label'] = country_label
        countries_m3u[country_id]['code'] = country_code
        countries_m3u[country_id]['channels'] = []

        # Iterate over channels of this country
        channels = importlib.import_module('lib.skeletons.' + country_id).menu
        for channel_id, channel_infos in list(channels.items()):

            print('\t* channel_id: ' + channel_id)

            # If this channel is disabled --> ignore this channel
            if not channel_infos.get('enabled', False):
                continue

            # If this channel is a folder (e.g. multi live) --> ignore this channel
            if 'resolver' not in channel_infos:
                continue

            channel_label = get_label(channel_id, channel_infos)

            # If we have mutliple languages
            # for this channel we need to add each language

            languages = []
            for language in channel_infos.get('available_languages', ['NO_LANGUAGE']):
                languages.append(language)

            # For each language we add the corresponding m3u entry
            for language in languages:

                channel_m3u = {
                    'resolver': channel_infos['resolver'].replace(':', '/'),
                    'logo': get_item_media_path(channel_infos["thumb"]),
                    'label': channel_label,
                    'params': {
                        'item_id': channel_id
                    },
                    'xmltv_id': channel_infos.get('xmltv_id', ''),
                    'group': country_label if 'm3u_group' not in channel_infos else country_label + ' ' + channel_infos['m3u_group'],
                    'group_all': country_label,
                    'add_in_all': True
                }

                if language != 'NO_LANGUAGE':
                    channel_m3u['label'] = channel_m3u['label'] + ' ' + language
                    channel_m3u['params']['language'] = language
                    channel_m3u['xmltv_id'] = channel_infos.get('xmltv_ids', {}).get(language, '')

                    # channel_group_coutry_wo
                    if language in channel_infos.get('m3u_groups', {}):
                        channel_m3u['group_wo'] = channel_infos['m3u_groups'][language]

                    # channel_order_wo
                    if language in channel_infos.get('m3u_orders', {}):
                        channel_m3u['order_wo'] = channel_infos['m3u_orders'][language]

                channel_order = channel_infos.get('m3u_order', 100)

                countries_m3u[country_id]['channels'].append((channel_order, channel_m3u))

    # Check if we have WO channels to copy in corresponding country (like Arte FR in Frenc M3U)
    print('\n# Copy WO channels in corresponding country if language is avaible')
    wo_channels = countries_m3u.get('wo_live', {}).get('channels', [])
    for channel_order, channel_m3u in wo_channels:
        if 'language' in channel_m3u['params']:
            language = channel_m3u['params']['language']
            language_id = language.lower() + '_live'
            if language_id in countries_m3u:
                print('\t* We need to add WO channel %s in %s country' % (channel_m3u['params']['item_id'], language_id))
                channel_m3u_copy = dict(channel_m3u)

                channel_m3u_copy['label'] = channel_m3u_copy['label'].replace(' ' + language, '')

                if 'group_wo' in channel_m3u_copy:
                    channel_m3u_copy['group'] = channel_m3u_copy['group_wo']
                else:
                    channel_m3u_copy['group'] = countries_m3u[language_id]['label']

                channel_order = channel_m3u_copy.get('order_wo', 100)

                channel_m3u_copy['add_in_all'] = False

                countries_m3u[language_id]['channels'].append((channel_order, channel_m3u_copy))

    # Now we can write in m3u files

    # Init m3u all file
    print("\n# Generate m3u all in " + LIVE_TV_M3U_ALL_FILEPATH)
    m3u_all = open(LIVE_TV_M3U_ALL_FILEPATH, "w")
    write_header(m3u_all)

    for country_id, country_dict in list(countries_m3u.items()):

        country_label = country_dict['label']
        country_code = country_dict['code']

        # Init m3u country file
        print("# Generate m3u of " + country_label + " in " +
              (LIVE_TV_M3U_COUTRY_FILEPATH % country_code))
        m3u_country = open((LIVE_TV_M3U_COUTRY_FILEPATH % country_code), "w")
        write_header(m3u_country)

        # Add the current country as comment
        m3u_country.write("# " + country_label + "\n")
        m3u_country.write("# " + country_id + "\n\n")
        m3u_all.write("# " + country_label + "\n")
        m3u_all.write("# " + country_id + "\n\n")

        channels = countries_m3u[country_id]['channels']
        channels = sorted(channels, key=lambda x: x[0])

        for index, (channel_order, channel_dict) in enumerate(channels):

            channel_id = channel_dict['params']['item_id']
            channel_label = channel_dict['label']
            channel_logo = channel_dict['logo']
            channel_params = channel_dict['params']
            channel_group = channel_dict['group']
            channel_group_all = channel_dict['group_all']
            channel_xmltv_id = channel_dict['xmltv_id']
            channel_resolver = channel_dict['resolver']

            query = urllib.parse.urlencode(channel_params)
            channel_url = PLUGIN_KODI_PATH + channel_resolver + '/?' + query

            channel_m3u_entry_country = M3U_ENTRY % (
                channel_xmltv_id, channel_logo, channel_group,
                channel_label, channel_url)
            m3u_country.write("##\t" + channel_label + "\n")
            m3u_country.write("##\t" + channel_id + "\n")
            m3u_country.write(channel_m3u_entry_country + "\n\n")

            if channel_dict['add_in_all']:
                channel_m3u_entry_all = M3U_ENTRY % (
                    channel_xmltv_id, channel_logo, channel_group_all,
                    channel_label, channel_url)
                m3u_all.write("##\t" + channel_label + "\n")
                m3u_all.write("##\t" + channel_id + "\n")
                m3u_all.write(channel_m3u_entry_all + "\n\n")

        m3u_all.write("\n\n")
        m3u_country.close()

    m3u_all.close()


def main():
    generate_m3u_files()
    print("\n# M3U files generation done! :-D")


if __name__ == '__main__':
    main()