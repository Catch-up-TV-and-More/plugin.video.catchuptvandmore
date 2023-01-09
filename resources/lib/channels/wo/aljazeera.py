# -*- coding: utf-8 -*-
# Copyright: (c) 2023, darodi
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import xbmcgui
# noinspection PyUnresolvedReferences
from codequick import Resolver, Script

from resources.lib import resolver_proxy


# TODO Replay add emissions


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    channels = [
        ('English', 'get_stream_youtube', 'GEumHK0hfdo'),
        ('الوثائقية', 'get_stream_youtube', 'TiPYdMXt_XI'),
        ('قناة مباشر', 'get_stream_youtube', 'eksOMqVMINo'),
        ('البث الحي', 'get_brightcove_video_json', '')
    ]

    selected_item = xbmcgui.Dialog().select(Script.localize(30174), list(map(lambda x: x[0], channels)))
    if selected_item == -1:
        return False

    selected_item = channels[selected_item]
    function_name = selected_item[1]
    if function_name == 'get_stream_youtube':
        return resolver_proxy.get_stream_youtube(plugin, selected_item[2], False)

    return resolver_proxy.get_brightcove_video_json(plugin, "665001584001", None, "5146642090001",
                                                    policy_key="BCpkADawqM2WV_cMXnGg7cQ_h8ZF7RlC8EyY4uVca2LT3ze4PrU4MCCuj3F7TA2rOsSXAXgLDcWKavBi2M5_R7HRDOAnsQ1OX4yzxA00cLv37ggu76kll4P_eX4",
                                                    download_mode=False, subtitles=None)
