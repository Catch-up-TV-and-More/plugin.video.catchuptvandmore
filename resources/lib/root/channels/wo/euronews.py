# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2017  SylvainCecchetto

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

import json
from resources.lib import utils
from resources.lib import common

# TO DO
# Replay add emissions
# Add info LIVE TV

URL_LIVE_API = 'http://%s.euronews.com/api/watchlive.json'
# Language


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)


def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_l':
        desired_language = common.PLUGIN.get_setting(
            params.channel_name + '.language')

        if desired_language == 'EN':
            url_live_json = URL_LIVE_API % 'www'
        elif desired_language == 'AR':
            url_live_json = URL_LIVE_API % 'arabic'
        else:
            url_live_json = URL_LIVE_API % desired_language.lower()

        file_path = utils.download_catalog(
            url_live_json,
            '%s_%s_live.json' % (
                params.channel_name, desired_language.lower())
        )
        json_live = open(file_path).read()
        json_parser = json.loads(json_live)
        url_2nd_json = json_parser["url"]

        file_path_2 = utils.download_catalog(
            url_2nd_json,
            '%s_%s_live_2.json' % (
                params.channel_name, desired_language.lower())
        )
        json_live_2 = open(file_path_2).read()
        json_parser_2 = json.loads(json_live_2)

        return json_parser_2["primary"]
