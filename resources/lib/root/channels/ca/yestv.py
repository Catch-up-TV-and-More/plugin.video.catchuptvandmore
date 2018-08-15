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
import re
from resources.lib import utils
from resources.lib import common

# TO DO
# Replay add emissions
# Add info LIVE TV

URL_LIVE = 'http://www.yestv.com/watch-live/?stream=%s'
# Town


LIVES_TOWN = {
    'Ontario': 'YESTV-ONT',
    'Alberta': 'YESTV-AB-C'
}


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)


def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_l':
        desired_region = common.PLUGIN.get_setting(
            params.channel_name + '.region')
        
        live_id = LIVES_TOWN[desired_region]

        live_html = utils.get_webcontent(
            URL_LIVE % live_id)
        url_live_2 = re.compile(
            'iframe src="(.*?) "').findall(live_html)[0]
        url_live_2 = url_live_2 + live_id
        live_html_2 = utils.get_webcontent(url_live_2)
        live_json = re.compile(
            'sources\:(.*?)\]\,').findall(live_html_2)[0]
        live_jsonpaser = json.loads(live_json + ']')

        url_live = 'http:' + live_jsonpaser[0]["file"]    

        return url_live