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

# Core imports
import importlib

# Kodi imports
from codequick import Script, utils
from kodi_six import xbmc
from kodi_six import xbmcgui

# Local imports
from resources.lib.vpn import add_vpn_context
import resources.lib.cq_utils as cqu
import resources.lib.favourites as fav
from resources.lib.labels import LABELS


"""Utility functions used to build a Kodi menu

"""


def get_sorted_menu(plugin, menu_id):
    """Get ordered 'menu_id' menu without disabled and hidden items

    Args:
        plugin (codequick.script.Script)
        menu_id (str): Menu to get (e.g. root)
    Returns:
        list<tuple> List of items (item_order, item_id, item_infos)
    """

    # The current menu to build contains
    # all the items present in the 'menu_id'
    # skeleton file
    current_menu = importlib.import_module('resources.lib.skeletons.' +
                                           menu_id).menu

    # Notify user for the new M3U Live TV feature
    if menu_id == "live_tv" and \
            cqu.get_kodi_version() >= 18 and \
            plugin.setting.get_boolean('show_live_tv_m3u_info'):

        r = xbmcgui.Dialog().yesno(plugin.localize(LABELS['Information']),
                                   plugin.localize(30605),
                                   plugin.localize(30606))
        if not r:
            plugin.setting['show_live_tv_m3u_info'] = False

    # Keep in memory the first menu taken
    # in order to provide a prefix when the user
    # add a favourite
    fav.guess_fav_prefix(menu_id)

    # First, we have to sort the current menu items
    # according to each item order and we have
    # to hide each disabled item
    menu = []
    for item_id, item_infos in list(current_menu.items()):

        add_item = True

        # If the item is enable
        if not Script.setting.get_boolean(item_id):
            add_item = False

        # If the desired language is not avaible
        if 'available_languages' in item_infos:
            desired_language = utils.ensure_unicode(Script.setting[item_id + '.language'])
            if desired_language not in item_infos['available_languages']:
                add_item = False

        if add_item:
            # Get order value in settings file
            item_order = Script.setting.get_int(item_id + '.order')

            item = (item_order, item_id, item_infos)

            menu.append(item)

    # We sort the menu according to the item_order values
    return sorted(menu, key=lambda x: x[0])


def add_context_menus_to_item(item, item_id, item_index, menu_id, menu_len, is_playable=False, item_infos={}):
    """Add basic context menus to the item

    Args:
        plugin (codequick.script.Script)
        item (codequick.listing.Listitem): Item for which we want to add context menus
        item_id (str): Id of the item
        item_index (int): Index of the item
        menu_id (str): Menu to get (e.g. root)
        menu_len (int): Length of the item menu
    """

    # Move up
    if item_index > 0:
        item.context.script(move_item,
                            Script.localize(LABELS['Move up']),
                            direction='up',
                            item_id=item_id,
                            menu_id=menu_id)

    # Move down
    if item_index < menu_len - 1:
        item.context.script(move_item,
                            Script.localize(LABELS['Move down']),
                            direction='down',
                            item_id=item_id,
                            menu_id=menu_id)

    # Hide
    item.context.script(hide_item,
                        Script.localize(LABELS['Hide']),
                        item_id=item_id)

    # Connect/Disconnect VPN
    add_vpn_context(item)

    # Add to add-on favourites
    item.context.script(fav.add_item_to_favourites,
                        Script.localize(LABELS['Add to add-on favourites']),
                        is_playable=is_playable,
                        item_infos=item_infos)

    return


"""Context menu callback functions

"""


@Script.register
def move_item(plugin, direction, item_id, menu_id):
    """Callback function of 'move item' conext menu

    Args:
        plugin (codequick.script.Script)
        direction (str): 'down' or 'up'
        item_id (str): item_id to move
        menu_id (str): menu_id of the item
    """
    if direction == 'down':
        offset = 1
    elif direction == 'up':
        offset = -1

    item_to_move_id = item_id
    item_to_move_order = plugin.setting.get_int(item_to_move_id + '.order')

    menu = get_sorted_menu(plugin, menu_id)

    for k in range(0, len(menu)):
        item = menu[k]
        item_id = item[1]
        if item_to_move_id == item_id:
            item_to_swap = menu[k + offset]
            item_to_swap_order = item_to_swap[0]
            item_to_swap_id = item_to_swap[1]
            plugin.setting[item_to_move_id + '.order'] = item_to_swap_order
            plugin.setting[item_to_swap_id + '.order'] = item_to_move_order
            xbmc.executebuiltin('XBMC.Container.Refresh()')
            break


@Script.register
def hide_item(plugin, item_id):
    """Callback function of 'hide item' context menu

    Args:
        plugin (codequick.script.Script)
        item_id (str): item_id to move
        menu_id (str): menu_id of the item
    """
    if plugin.setting.get_boolean('show_hidden_items_information'):
        xbmcgui.Dialog().ok(
            plugin.localize(LABELS['Information']),
            plugin.localize(
                LABELS['To re-enable hidden items go to the plugin settings']))
        plugin.setting['show_hidden_items_information'] = False

    plugin.setting[item_id] = False
    xbmc.executebuiltin('XBMC.Container.Refresh()')
