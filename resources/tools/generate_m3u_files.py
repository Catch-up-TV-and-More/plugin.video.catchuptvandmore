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

import lib.skeleton as sk
from lib.labels import LABELS

LIVE_TV_M3U_ALL_FILEPATH = "../m3u/live_tv_all_auto_generated.m3u"

EN_STRINGS_PO_FILEPATH = "../language/resource.language.en_gb/strings.po"


LOGO_URL = "https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore/raw/master/resources/media/channels/%s/%s"
# arg0: country_code (fr, nl, jp, ...)
# arg1: channel_id (tf1, france2, ...)

PLUGIN_PATH = "plugin://plugin.video.catchuptvandmore/main/live_bridge/?item_id=%sitem_module=%s"
# arg0: item_id (tf1, france2, ...)
# arg1: module (resources.lib.channels.fr.mytf1, ...)

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



# Return string label from item_id
def get_label(item_id):
    label = LABELS[item_id]
    if isinstance(label, int):
        if ('#' + str(label) ) in en_strings_po:
            return en_strings_po['#' + str(label)]
        else:
            return item_id    
    return label


# Write M3U header in file
def write_header(file):
    file.write("#EXTM3U tvg-shift=0\n\n")



# Generate live_tv_all.m3u
def generate_m3u_all():
 
    m3u_all = open(LIVE_TV_M3U_ALL_FILEPATH, "w") 

    write_header(m3u_all)

    # Iterate over countries
    for country_id, country_infos in eval('sk.LIVE_TV').items():
        
        country_label = get_label(country_id)

        print('\ncountry_id: ' + country_id)
        print('\ncountry_label: ' + country_label)
        
        m3u_all.write("# " + country_label + "\n")
        m3u_all.write("# " + country_id + "\n\n")

        # Iterate over channels
        for channel_id, channel_infos in eval('sk.' + country_id.upper()).items():
            
            channel_label = get_label(channel_id)

            print('\n\tchannel_id: ' + channel_id)
            print('\t\tchannel_label: ' + channel_label)

            if isinstance(channel_label, str):
                m3u_all.write("##\t" + channel_label + "\n")
            else:
                m3u_all.write("##\tMANUAL_TODO: " + channel_id + "\n")
            m3u_all.write("##\t" + channel_id + "\n")

            
            tvg_id = ""
            tvg_logo = LOGO_URL % (channel_infos["thumb"][1], channel_infos["thumb"][2])
            group_title = country_label
            channel_url = PLUGIN_PATH % ( "", channel_infos["module"])

            m3u_entry = M3U_ENTRY % (tvg_id, tvg_logo, group_title, channel_label, channel_url)
            m3u_all.write(m3u_entry + "\n\n")

        m3u_all.write("\n\n")
            




    m3u_all.close()


generate_m3u_all()










