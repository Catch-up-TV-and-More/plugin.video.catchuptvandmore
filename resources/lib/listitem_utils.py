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

from codequick import Script

from resources.lib.favourites import add_item_to_favourites
from resources.lib.labels import LABELS


def item_post_treatment(item, is_playable=False, is_downloadable=False):
    """Add needed context menus to 'item'

    Args:
        is_playable (bool): If 'item' is playable
        is_downloadable (bool): If 'item' is downloadable
    Returns:
        str: (translated) label of 'item_id'
    """

    # Add `Download` context menu to 'item' if 'item' is downloadable
    if is_downloadable:
        item.context.script(item.path,
                            Script.localize(LABELS['Download']),
                            download_mode=True,
                            **item.params)

    # Add `Add to add-on favourites` context menu to 'item'
    item.context.script(add_item_to_favourites,
                        Script.localize(LABELS['Add to add-on favourites']),
                        is_playable=is_playable)

    return
