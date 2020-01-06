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
from kodi_six import xbmcvfs

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
