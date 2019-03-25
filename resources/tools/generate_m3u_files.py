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
import polib
import sys
sys.path.append('..')

import mock_codequick
import urllib

import lib.skeleton as sk
from lib.labels import LABELS


LIVE_TV_M3U_ALL_FILEPATH = "../m3u/live_tv_all_auto_generated.m3u"

LIVE_TV_M3U_COUTRY_FILEPATH = "../m3u/live_tv_%s_auto_generated.m3u"
# arg0: country_code (fr, nl, jp, ...)




EN_STRINGS_PO_FILEPATH = "../language/resource.language.en_gb/strings.po"


LOGO_URL = "https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore/raw/master/resources/media/channels/%s/%s"
# arg0: country_code (fr, nl, jp, ...)
# arg1: channel_id (tf1, france2, ...)

PLUGIN_QUERY = "item_id=%s&item_module=%s&item_dict=%s"
# arg0: item_id (tf1, france2, ...)
# arg1: module (resources.lib.channels.fr.mytf1, ...)
# arg2: item_dict ({'language': 'FR'})

PLUGIN_LIVE_BRIDGE_PATH = "plugin://plugin.video.catchuptvandmore/main/live_bridge/"


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
    'realmadridtv': 'Realmadrid TV'
}


# Return string label from item_id
def get_label(item_id):
    label = LABELS[item_id]

    # strings.po case
    if isinstance(label, int):
        if ('#' + str(label) ) in en_strings_po:
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
def generation_m3u(is_m3u_all):

    if is_m3u_all:
        print ("Generate m3u all in " + LIVE_TV_M3U_ALL_FILEPATH)
        m3u = open(LIVE_TV_M3U_ALL_FILEPATH, "w") 

        write_header(m3u)


    # Iterate over countries
    for country_id, country_infos in eval('sk.LIVE_TV').items():
        
        country_label = get_label(country_id)
        country_code =  country_id.replace('_live', '')
        
        if not is_m3u_all:
            print ("Generate m3u of " + country_label + " in " + (LIVE_TV_M3U_COUTRY_FILEPATH % country_code))
            m3u = open((LIVE_TV_M3U_COUTRY_FILEPATH % country_code), "w") 
            write_header(m3u)

        print('\ncountry_id: ' + country_id)
        #print('\ncountry_label: ' + country_label)
        
        m3u.write("# " + country_label + "\n")
        m3u.write("# " + country_id + "\n\n")

        channel_entries = []


        # Iterate over channels
        for channel_id, channel_infos in eval('sk.' + country_id.upper()).items():
            
            channel_label = get_label(channel_id)
            print('\n\tchannel_id: ' + channel_id)
            # print('\t\tchannel_label: ' + channel_label)

            languages = []
            # Key: Label to append
            # Value: item_dict value

            if 'available_languages' in channel_infos:
                for language in channel_infos['available_languages']:
                    languages.append({
                        'language_label': ' ' + language,
                        'language_dict' : "{'language':'" + language + "'}"
                        }
                    )
            else:
                languages.append({
                    'language_label': '',
                    'language_dict' : '{}'
                    }
                )


            for language in languages:
                
                m3u_group = country_label
                if 'm3u_group' in channel_infos:
                    m3u_group = m3u_group + " " + channel_infos['m3u_group']
                m3u_order = channel_infos.get('m3u_order', 100)
                xmltv_id = channel_infos.get('xmltv_id', '')

                channel_logo = LOGO_URL % (channel_infos["thumb"][1], channel_infos["thumb"][2])
                
                channel_dict = language['language_dict']

                query = PLUGIN_QUERY % (channel_id, channel_infos["module"], channel_dict)
                channel_url = PLUGIN_LIVE_BRIDGE_PATH + "?" + query

                m3u_entry = M3U_ENTRY % (xmltv_id, channel_logo, m3u_group, channel_label + language['language_label'], channel_url)

                channel_entry = (m3u_order, channel_label + language['language_label'], channel_id, m3u_entry)
                channel_entries.append(channel_entry)


        # Insert each ordered channels
        channel_entries = sorted(channel_entries, key=lambda x: x[0])

        for index, (m3u_order, channel_label, channel_id, m3u_entry) in enumerate(channel_entries):
            
            m3u.write("##\t" + channel_label + "\n")
            m3u.write("##\t" + channel_id + "\n")
            m3u.write(m3u_entry + "\n\n")
             

        if is_m3u_all:
            m3u.write("\n\n")
        else:
            m3u.close()

    if is_m3u_all:
        m3u.close()






def main():

    generation_m3u(True)

    generation_m3u(False)
    
    print("\nM3U files generation done! :-D")


if __name__ == '__main__':
    main()









