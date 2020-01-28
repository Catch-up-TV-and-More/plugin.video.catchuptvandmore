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

import os
import json
import importlib
from builtins import str
from builtins import range
from kodi_six import xbmcvfs
import xml.etree.ElementTree as ET


from codequick import storage, Script, listing


def migrate_from_pickled_fav():
    """
    This function moves existing pickled favourites in
    the new json file used for the favourites.
    The new format (json) appeared in 0.2.17~beta04
    All user with version >= 0.2.17 will use favourites in the JSON format
    Maybe we can remove the migration check on version 0.2.20?
    """

    # Move all pickled existing favs in json file
    fav_pickle_fp = os.path.join(Script.get_info('profile'), "favourites.pickle")
    if xbmcvfs.exists(fav_pickle_fp):
        Script.log('Start favourites migration from pickle file to json file')
        new_fav_dict = {}
        with storage.PersistentDict("favourites.pickle") as db:
            new_fav_dict = dict(db)
        # Fix old fav
        for item_hash, item_dict in new_fav_dict.items():
            if 'params' in item_dict and isinstance(item_dict['params'], listing.Params):
                new_fav_dict[item_hash]['params'] = dict(new_fav_dict[item_hash]['params'])
                try:
                    del new_fav_dict[item_hash]['params']['item_dict']['params']
                except Exception:
                    pass
            if 'properties' in item_dict:
                if isinstance(item_dict['properties'], listing.Property):
                    new_fav_dict[item_hash]['properties'] = dict(new_fav_dict[item_hash]['properties'])
        fav_json_fp = os.path.join(Script.get_info('profile'), "favourites.json")
        with open(fav_json_fp, 'w') as f:
            json.dump(new_fav_dict, f, indent=4)
        xbmcvfs.delete(fav_pickle_fp)


def migrate_old_menus_settings(menus_settings_fp):
    """
    This function moves old user settings concerning hidden menu
    and items order in
    the new json file used for that purpose.
    The feature (json) appeared in 0.2.17~betaXX
    All user with version >= 0.2.17 will use item settings in the JSON format
    Maybe we can remove the migration check on version 0.2.20?
    """

    # If the json file already exists, the migration has already be done
    if xbmcvfs.exists(menus_settings_fp):
        return

    # We directly read the XML setting file (faster than 'xbmcaddon.Addon().getSetting(s)')
    addon_settings_fp = os.path.join(Script.get_info('profile'), "settings.xml")
    if not xbmcvfs.exists(addon_settings_fp):
        return

    Script.log('Start item settings migration to json file')
    j = {}

    skeletons = [
        "root",
        "live_tv",
        "replay",
        'websites',
        "fr_live",
        "ch_live",
        "uk_live",
        "wo_live",
        "be_live",
        "jp_live",
        "ca_live",
        "us_live",
        "pl_live",
        "es_live",
        "tn_live",
        "it_live",
        "nl_live",
        "cn_live",
        "fr_replay",
        "ch_replay",
        "uk_replay",
        "wo_replay",
        "be_replay",
        "jp_replay",
        "ca_replay",
        "us_replay",
        "es_replay",
        "tn_replay",
        "it_replay",
        "nl_replay",
        "cn_replay"
    ]

    tree = ET.parse(addon_settings_fp)
    old_settings = {}
    for elem in tree.findall('setting'):
        if 'id' in elem.attrib:
            setting_id = elem.attrib['id']
            if 'value' in elem.attrib:
                # Kodi 17 case
                setting_value = elem.attrib['value']
            else:
                # Kodi 18 and 19 case
                setting_value = elem.text
            # try:
            #     print('Setting: "{}" --> "{}"'.format(setting_id, setting_value))
            # except Exception:
            #     pass
            old_settings[setting_id] = setting_value

    for skeleton in skeletons:
        current_menu = importlib.import_module('resources.lib.skeletons.' +
                                               skeleton).menu
        for setting_id, setting_value in old_settings.items():
            order = False
            if '.order' in setting_id:
                setting_id = setting_id.split('.')[0]
                order = True
            if setting_id in current_menu:
                item_infos = current_menu[setting_id]
                if setting_value != "":
                    if order:
                        if item_infos['order'] != int(setting_value):
                            if skeleton not in j:
                                j[skeleton] = {}
                            if setting_id not in j[skeleton]:
                                j[skeleton][setting_id] = {}
                            j[skeleton][setting_id]['order'] = int(setting_value)
                    else:
                        if setting_value.lower() == "false" and item_infos['enabled'] is True:
                            if skeleton not in j:
                                j[skeleton] = {}
                            if setting_id not in j[skeleton]:
                                j[skeleton][setting_id] = {}
                            j[skeleton][setting_id]['hidden'] = True



    # Save new item settings json
    with open(menus_settings_fp, 'w') as f:
        json.dump(j, f, indent=4)
