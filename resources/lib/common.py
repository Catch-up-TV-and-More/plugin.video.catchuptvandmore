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
import numbers
import time
from codequick.script import Script
from codequick.utils import ensure_native_str

from kodi_six import xbmc

from resources.lib.labels import LABELS
from resources.lib.entrypoint_utils import get_params_in_query


def get_item_label(item_id):
    """Get (translated) label of 'item_id'

    Args:
        item_id (str)
    Returns:
        str: (translated) label of 'item_id'
    """
    label = item_id
    if item_id in LABELS:
        label = LABELS[item_id]
        if isinstance(label, int):
            label = Script.localize(label)
    return label


def get_item_media_path(item_media_path):
    """Get full path or URL of an item_media

    Args:
        item_media_path (str or list): Partial media path of the item (e.g. channels/fr/tf1.png)
    Returns:
        str: Full path or URL of the item_pedia
    """
    full_path = ''

    # Local image in ressources/media folder
    if type(item_media_path) is list:
        full_path = os.path.join(Script.get_info("path"), "resources", "media",
                                 *(item_media_path))

    # Remote image with complete URL
    elif 'http' in item_media_path:
        full_path = item_media_path

    # Remote image on our images repo
    else:
        full_path = 'https://github.com/Catch-up-TV-and-More/images/raw/master/' + item_media_path

    return ensure_native_str(full_path)


def get_selected_item_art():
    """Get 'art' dict of the selected item in the current Kodi menu

    Returns:
        dict: Selected item 'art' dict
    """
    art = {}
    for art_type in ['thumb', 'poster', 'banner', 'fanart', 'clearart', 'clearlogo', 'landscape', 'icon']:
        v = xbmc.getInfoLabel('ListItem.Art({})'.format(art_type))
        art[art_type] = v
    return art


def get_selected_item_label():
    """Get label the selected item in the current Kodi menu

    Returns:
        str: Selected item label
    """
    return xbmc.getInfoLabel('ListItem.Label')


def get_selected_item_params():
    """Get 'params' dict of the selected item in the current Kodi menu

    Returns:
        dict: Selected item 'params' dict
    """
    path = xbmc.getInfoLabel('ListItem.FilenameAndPath')
    return get_params_in_query(path)


def get_selected_item_stream():
    """Get 'stream' dict of the selected item in the current Kodi menu

    Returns:
        dict: Selected item 'stream' dict
    """
    stream = {}
    stream['video_codec'] = xbmc.getInfoLabel('ListItem.VideoCodec')
    stream['aspect'] = xbmc.getInfoLabel('ListItem.VideoAspect')
    stream['aspect'] = float(stream['aspect']) if stream['aspect'] != '' else stream['aspect']
    # stream['width'] (TODO)
    # stream['channels'] (TODO)
    stream['audio_codec'] = xbmc.getInfoLabel('ListItem.VideoCodec')
    stream['audio_language'] = xbmc.getInfoLabel('ListItem.AudioLanguage')
    stream['subtitle_language'] = xbmc.getInfoLabel('ListItem.SubtitleLanguage')
    return stream


def get_selected_item_info():
    """Get 'info' dict of the selected item in the current Kodi menu

    Returns:
        dict: Selected item 'info' dict
    """
    info = {}
    info['plot'] = xbmc.getInfoLabel('ListItem.Plot')
    return info


def old_div(a, b):
    """Python 2 and 3 Integer division cheat (https://python-future.org/compatible_idioms.html#division)

    """
    if isinstance(a, numbers.Integral) and isinstance(b, numbers.Integral):
        return a // b
    else:
        return a / b


def current_timestamp():
    """Get current timestamp (Unix time, the same given here https://timestamp.online)

    Returns:
        float: Current timestamp
    """
    return time.time()
