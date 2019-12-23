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
from builtins import str
from builtins import range
from kodi_six import xbmc
from kodi_six import xbmcgui
from kodi_six import xbmcvfs

from codequick import utils, storage, Script, listing
from hashlib import md5

from resources.lib.labels import LABELS
from resources.lib import common
import resources.lib.mem_storage as mem_storage

FAV_JSON_FP = os.path.join(Script.get_info('profile'), "favourites.json")


def migrate_from_pickled_fav():
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
        save_fav_dict_in_json(new_fav_dict)
        xbmcvfs.delete(fav_pickle_fp)


def get_fav_dict_from_json():
    migrate_from_pickled_fav()
    if not xbmcvfs.exists(FAV_JSON_FP):
        return {}
    try:
        with open(FAV_JSON_FP) as f:
            return json.load(f)
    except Exception:
        Script.log('Failed to load favourites json data')
        xbmcvfs.delete(FAV_JSON_FP)
        return {}


def save_fav_dict_in_json(fav_dict):
    with open(FAV_JSON_FP, 'w') as f:
        json.dump(fav_dict, f, indent=4)


def guess_fav_prefix(item_id):
    """
    When the use add a favourite,
    guess the prefix to add for the
    favourite label according to the
    current main category
    """
    prefix = 'empty'
    if item_id == 'live_tv':
        prefix = Script.localize(LABELS['live_tv'])
    elif item_id == 'replay':
        prefix = Script.localize(LABELS['replay'])
    elif item_id == 'websites':
        prefix = Script.localize(LABELS['websites'])
    elif item_id == 'root':
        prefix = ''
    if prefix != 'empty':
        s = mem_storage.MemStorage('fav')
        s['prefix'] = prefix


@Script.register
def add_item_to_favourites(plugin, item_dict={}, **kwargs):
    """
    Callback function called when the user click
    on 'add item to favourite' from an item
    context menu
    """

    if 'channel_infos' in kwargs and \
            kwargs['channel_infos'] is not None:

        # This item come from tv_guide_menu
        # We need to remove guide TV related
        # elements

        item_id = item_dict['params']['item_id']
        label = item_id
        if item_id in LABELS:
            label = LABELS[item_id]
            if isinstance(label, int):
                label = Script.localize(label)
        item_dict['label'] = label

        if 'thumb' in kwargs['channel_infos']:
            item_dict['art']["thumb"] = common.get_item_media_path(
                kwargs['channel_infos']['thumb'])

        if 'fanart' in kwargs['channel_infos']:
            item_dict['art']["fanart"] = common.get_item_media_path(
                kwargs['channel_infos']['fanart'])

        item_dict['info'] = {}

    # Extract the callback
    item_path = xbmc.getInfoLabel('ListItem.Path')
    item_dict['callback'] = item_path.replace(
        'plugin://plugin.video.catchuptvandmore', '')

    s = mem_storage.MemStorage('fav')
    prefix = ''
    try:
        prefix = s['prefix']
    except KeyError:
        pass

    label_proposal = item_dict['label']
    if prefix != '':
        label_proposal = prefix + ' - ' + label_proposal

    # Ask the user to edit the label
    item_dict['label'] = utils.keyboard(
        plugin.localize(LABELS['Favorite name']), label_proposal)

    # If user aborded do not add this item to favourite
    if item_dict['label'] == '':
        return False

    # Compute fav hash
    item_hash = md5(str(item_dict).encode('utf-8')).hexdigest()

    # Add this item to favourites json file
    fav_dict = get_fav_dict_from_json()
    item_dict['params']['order'] = len(fav_dict)

    fav_dict[item_hash] = item_dict

    # Save json file with new fav_dict
    save_fav_dict_in_json(fav_dict)

    Script.notify(Script.localize(30033), Script.localize(30805), display_time=7000)


@Script.register
def rename_favourite_item(plugin, item_hash):
    """
    Callback function called when the user click
    on 'rename' from a favourite item
    context menu
    """
    item_label = utils.keyboard(plugin.localize(LABELS['Favorite name']),
                                xbmc.getInfoLabel('ListItem.Label'))

    # If user aborded do not edit this item
    if item_label == '':
        return False
    fav_dict = get_fav_dict_from_json()
    fav_dict[item_hash]['label'] = item_label
    save_fav_dict_in_json(fav_dict)
    xbmc.executebuiltin('XBMC.Container.Refresh()')


@Script.register
def remove_favourite_item(plugin, item_hash):
    """
    Callback function called when the user click
    on 'remove' from a favourite item
    context menu
    """
    fav_dict = get_fav_dict_from_json()
    del fav_dict[item_hash]

    # We need to fix the order param
    # in order to not break the move up/down action
    menu = []
    for item_hash, item_dict in list(fav_dict.items()):
        item = (item_dict['params']['order'], item_hash)

        menu.append(item)
    menu = sorted(menu, key=lambda x: x[0])

    for k in range(0, len(menu)):
        item = menu[k]
        item_hash = item[1]
        fav_dict[item_hash]['params']['order'] = k
    save_fav_dict_in_json(fav_dict)
    xbmc.executebuiltin('XBMC.Container.Refresh()')


@Script.register
def move_favourite_item(plugin, direction, item_hash):
    """
    Callback function called when the user click
    on 'Move up/down' from a favourite item
    context menu
    """
    if direction == 'down':
        offset = 1
    elif direction == 'up':
        offset = -1

    fav_dict = get_fav_dict_from_json()
    item_to_move_id = item_hash
    item_to_move_order = fav_dict[item_hash]['params']['order']

    menu = []
    for item_hash, item_dict in list(fav_dict.items()):
        item = (item_dict['params']['order'], item_hash, item_dict)

        menu.append(item)
    menu = sorted(menu, key=lambda x: x[0])

    for k in range(0, len(menu)):
        item = menu[k]
        item_hash = item[1]
        if item_to_move_id == item_hash:
            item_to_swap = menu[k + offset]
            item_to_swap_order = item_to_swap[0]
            item_to_swap_id = item_to_swap[1]
            fav_dict[item_to_move_id]['params']['order'] = item_to_swap_order
            fav_dict[item_to_swap_id]['params']['order'] = item_to_move_order
            save_fav_dict_in_json(fav_dict)
            xbmc.executebuiltin('XBMC.Container.Refresh()')
            break

    return False


def add_fav_context(item, item_dict, **kwargs):
    """
    Add the 'Add to add-on favourites'
    context menu to item
    """
    if kwargs.get('is_playable', False):
        item_dict['params']['is_folder'] = False
        item_dict['params']['is_playable'] = True
    else:
        item_dict['params']['is_folder'] = True
        item_dict['params']['is_playable'] = False

    item.context.script(add_item_to_favourites,
                        Script.localize(LABELS['Add to add-on favourites']),
                        item_dict=item_dict,
                        **kwargs)


def ask_to_delete_error_fav_item(params):
    """
    Suggest user to delete
    the fav item that trigger the error
    """
    r = xbmcgui.Dialog().yesno(Script.localize(LABELS['Information']),
                               Script.localize(30807))
    if r:
        remove_favourite_item(plugin=None, item_hash=params['item_hash'])


@Script.register
def delete_favourites(plugin):
    """
    Callback function of 'Delete favourites'
    setting button
    """

    Script.log('Delete favourites db')
    xbmcvfs.delete(os.path.join(Script.get_info('profile'), 'favourites.pickle'))
    xbmcvfs.delete(os.path.join(Script.get_info('profile'), 'favourites.json'))
    Script.notify(Script.localize(30374), '')
