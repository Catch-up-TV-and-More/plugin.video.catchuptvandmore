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

from builtins import str
import polib
import sys
import mock

sys.path.append('../plugin.video.catchuptvandmore')
sys.path.append('../plugin.video.catchuptvandmore/resources')
sys.path.append('../plugin.video.catchuptvandmore/resources/lib')

sys.modules['codequick'] = mock.MagicMock()
sys.modules['resources.lib.codequick'] = mock.MagicMock()

import importlib
import os


LIVE_TV_M3U_ALL_FILEPATH = "../plugin.video.catchuptvandmore/resources/m3u/live_tv_all.m3u"

LIVE_TV_M3U_COUTRY_FILEPATH = "../plugin.video.catchuptvandmore/resources/m3u/live_tv_%s.m3u"
# arg0: country_code (fr, nl, jp, ...)

EN_STRINGS_PO_FILEPATH = "../plugin.video.catchuptvandmore/resources/language/resource.language.en_gb/strings.po"

# NOT USED ANYMORE
# LOGO_URL = "https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore/raw/%s/resources/media/channels/%s/%s"
# arg0: branch (dev or master)
# arg1: country_code (fr, nl, jp, ...)
# arg2: channel_id (tf1, france2, ...)

PLUGIN_QUERY = "%s/?item_id=%s&item_module=%s&item_dict=%s"
# arg0: callback
# arg1: item_id (tf1, france2, ...)
# arg2: module (resources.lib.channels.fr.mytf1, ...)
# arg3: item_dict ({'language': 'FR'})

PLUGIN_LIVE_BRIDGE_PATH = "plugin://plugin.video.catchuptvandmore/resources/lib/main/"

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


def get_labels_dict():
    labels_py_fp = '../plugin.video.catchuptvandmore/resources/lib/labels.py'
    lines = []
    with open(labels_py_fp, 'r') as f:
        take_line = False
        for line in f.readlines():
            if 'LABELS = {' in line:
                take_line = True
                line = '{'

            if 'Script.' in line:
                line = "'FOO',"

            if take_line:
                lines.append(line)

            if '}' in line:
                take_line = False
    labels_dict_s = '\n'.join(lines)
    return eval(labels_dict_s)


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
def get_label(item_id, labels):
    label = labels[item_id]

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

    # Label given in labels.py case
    elif isinstance(label, str):
        return label

    else:
        print('\nNeed to add ' + item_id + ' label in MANUAL_LABELS')
        exit(-1)


# Write M3U header in file
def write_header(file):
    file.write("#EXTM3U tvg-shift=0\n\n")


# Generate m3u files
def generate_m3u_files(labels):

    m3u_entries = {}

    # Iterate over countries
    live_tv = importlib.import_module('lib.skeletons.live_tv').menu
    for country_id, country_infos in list(live_tv.items()):

        country_label = get_label(country_id, labels)
        country_code = country_id.replace('_live', '')

        print('\ncountry_id: ' + country_id)
        # print('\ncountry_label: ' + country_label)

        if country_id not in m3u_entries:
            m3u_entries[country_id] = {}
            m3u_entries[country_id]['country_label'] = country_label
            m3u_entries[country_id]['country_code'] = country_code
            m3u_entries[country_id]['channels'] = []

        # Iterate over channels
        country_channels = importlib.import_module('lib.skeletons.' +
                                                   country_id).menu
        for channel_id, channel_infos in list(country_channels.items()):

            channel_label = get_label(channel_id, labels)
            print('\n\tchannel_id: ' + channel_id)
            # print('\t\tchannel_label: ' + channel_label)

            # If we have mutliple languages
            # for this channel we need to add each language

            languages = []
            # Key: Label to append
            # Value: custom item_dict

            if 'enabled' in channel_infos:
                if not channel_infos['enabled']:
                    continue

            if 'available_languages' in channel_infos:
                for language in channel_infos['available_languages']:
                    languages.append({
                        'language_code':
                        language.lower(),
                        'language_label':
                        ' ' + language,
                        'language_dict':
                        '{"language":"' + language + '"}'
                    })
            else:
                languages.append({
                    'language_code': '',
                    'language_label': '',
                    'language_dict': '{}'
                })

            # For each language we add the corresponding m3u entry
            for language in languages:

                channel_m3u_dict = {}

                # channe_id
                channel_m3u_dict['channel_id'] = channel_id

                # channe_module
                channel_m3u_dict['channel_module'] = channel_infos['module']

                # Is the call back is not live_bridge we skip :-/
                channel_m3u_dict['channel_callback'] = channel_infos[
                    'callback']
                if channel_m3u_dict['channel_callback'] != 'live_bridge':
                    continue

                # channel_logo
                # channel_m3u_dict['channel_logo'] = LOGO_URL % (current_branch, channel_infos["thumb"][1], channel_infos["thumb"][2])
                channel_m3u_dict['channel_logo'] = get_item_media_path(
                    channel_infos["thumb"])

                # channel_label
                channel_m3u_dict['channel_label'] = channel_label + language[
                    'language_label']

                # channel_dict
                channel_m3u_dict['channel_item_dict'] = language[
                    'language_dict']

                # channel_group_coutry
                channel_m3u_dict['channel_group_country'] = country_label
                if 'm3u_group' in channel_infos:
                    channel_m3u_dict[
                        'channel_group_country'] = channel_m3u_dict[
                            'channel_group_country'] + " " + channel_infos[
                                'm3u_group']

                # channel_group_all
                channel_m3u_dict['channel_group_all'] = country_label

                # channel_xmltv_id
                channel_m3u_dict['channel_xmltv_id'] = ''
                if 'xmltv_ids' in channel_infos:
                    if language['language_code'] in channel_infos['xmltv_ids']:
                        channel_m3u_dict['channel_xmltv_id'] = channel_infos[
                            'xmltv_ids'][language['language_code']]
                elif 'xmltv_id' in channel_infos:
                    channel_m3u_dict['channel_xmltv_id'] = channel_infos[
                        'xmltv_id']

                channel_m3u_dict['add_in_all'] = True

                # channel_order
                channel_order = channel_infos.get('m3u_order', 100)

                m3u_entries[country_id]['channels'].append(
                    (channel_order, channel_m3u_dict))

        # Add WO channels if needed (e.g. Arte FR in the French M3U)
        wo_live = importlib.import_module('lib.skeletons.wo_live').menu
        for channel_wo_id, channel_wo_infos in list(wo_live.items()):
            channel_can_be_added = False
            if 'available_languages' in channel_wo_infos:
                if country_code.upper(
                ) in channel_wo_infos['available_languages']:
                    channel_can_be_added = True

            if channel_can_be_added:

                channel_wo_label = get_label(channel_wo_id, labels)

                channel_m3u_dict = {}

                # channe_id
                channel_m3u_dict['channel_id'] = channel_wo_id

                # channe_module
                channel_m3u_dict['channel_module'] = channel_wo_infos['module']

                # Is the call back is not live_bridge we skip :-/
                channel_m3u_dict['channel_callback'] = channel_wo_infos[
                    'callback']
                if channel_m3u_dict['channel_callback'] != 'live_bridge':
                    continue

                # channel_logo
                # channel_m3u_dict['channel_logo'] = LOGO_URL % (current_branch, channel_wo_infos["thumb"][1], channel_wo_infos["thumb"][2])
                channel_m3u_dict['channel_logo'] = get_item_media_path(
                    channel_wo_infos["thumb"])

                # channel_label
                channel_m3u_dict['channel_label'] = channel_wo_label

                # channel_dict
                channel_m3u_dict[
                    'channel_item_dict'] = '{"language":"' + country_code.upper() + '"}'

                # channel_group_coutry
                channel_m3u_dict['channel_group_country'] = country_label
                if 'm3u_groups' in channel_wo_infos:
                    if country_code in channel_wo_infos['m3u_groups']:
                        channel_m3u_dict[
                            'channel_group_country'] = channel_wo_infos[
                                'm3u_groups'][country_code]
                elif 'm3u_group' in channel_wo_infos:
                    channel_m3u_dict[
                        'channel_group_country'] = channel_m3u_dict[
                            'channel_group_country'] + " " + channel_wo_infos[
                                'm3u_group']

                # channel_group_all
                channel_m3u_dict['channel_group_all'] = ''  # Not used

                # channel_xmltv_id
                channel_m3u_dict['channel_xmltv_id'] = ''
                if 'xmltv_ids' in channel_wo_infos:
                    if country_code in channel_wo_infos['xmltv_ids']:
                        channel_m3u_dict[
                            'channel_xmltv_id'] = channel_wo_infos[
                                'xmltv_ids'][country_code]
                elif 'xmltv_id' in channel_wo_infos:
                    channel_m3u_dict['channel_xmltv_id'] = channel_wo_infos[
                        'xmltv_id']

                # channel_order
                channel_order = 100
                if 'm3u_orders' in channel_wo_infos:
                    if country_code in channel_wo_infos['m3u_orders']:
                        channel_order = channel_wo_infos['m3u_orders'][
                            country_code]
                elif 'm3u_order' in channel_wo_infos:
                    channel_order = channel_wo_infos['m3u_order']

                channel_m3u_dict['add_in_all'] = False

                m3u_entries[country_id]['channels'].append(
                    (channel_order, channel_m3u_dict))

    # Now we can write in m3u files

    # Init m3u all file
    print("Generate m3u all in " + LIVE_TV_M3U_ALL_FILEPATH)
    m3u_all = open(LIVE_TV_M3U_ALL_FILEPATH, "w")
    write_header(m3u_all)

    for country_id, country_dict in list(m3u_entries.items()):

        country_label = country_dict['country_label']
        country_code = country_dict['country_code']

        # Init m3u country file
        print("Generate m3u of " + country_label + " in " +
              (LIVE_TV_M3U_COUTRY_FILEPATH % country_code))
        m3u_country = open((LIVE_TV_M3U_COUTRY_FILEPATH % country_code), "w")
        write_header(m3u_country)

        # Add the current country as comment
        m3u_country.write("# " + country_label + "\n")
        m3u_country.write("# " + country_id + "\n\n")
        m3u_all.write("# " + country_label + "\n")
        m3u_all.write("# " + country_id + "\n\n")

        channels = m3u_entries[country_id]['channels']
        channels = sorted(channels, key=lambda x: x[0])

        for index, (channel_order, channel_dict) in enumerate(channels):

            channel_id = channel_dict['channel_id']
            channel_module = channel_dict['channel_module']
            channel_label = channel_dict['channel_label']
            channel_logo = channel_dict['channel_logo']
            channel_item_dict = channel_dict['channel_item_dict']
            channel_group_country = channel_dict['channel_group_country']
            channel_group_all = channel_dict['channel_group_all']
            channel_xmltv_id = channel_dict['channel_xmltv_id']
            channel_callback = channel_dict['channel_callback']

            query = PLUGIN_QUERY % (channel_callback, channel_id,
                                    channel_module, channel_item_dict)
            channel_url = PLUGIN_LIVE_BRIDGE_PATH + query

            channel_m3u_entry_country = M3U_ENTRY % (
                channel_xmltv_id, channel_logo, channel_group_country,
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
    labels = get_labels_dict()
    generate_m3u_files(labels)
    print("\nM3U files generation done! :-D")


if __name__ == '__main__':
    main()
