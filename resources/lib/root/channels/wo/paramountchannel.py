# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2018  SylvainCecchetto

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
from resources.lib import resolver
from resources.lib import common

# TO DO
# Add Replay ES, FR, ....

DESIRED_LANGUAGE = common.PLUGIN.get_setting('paramountchannel.language')

URL_ROOT = 'http://www.paramountchannel.%s' % DESIRED_LANGUAGE.lower()

URL_LIVE_ES = URL_ROOT + '/programacion/en-directo'

URL_LIVE_IT = URL_ROOT + '/tv/diretta'

URL_LIVE_URI = 'http://media.mtvnservices.com/pmt/e1/access/index.html?uri=%s&configtype=edge'

def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
        params.next = "list_shows_1"
        params["page"] = "0"
        return list_shows(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    return None

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)


def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_l':
        if DESIRED_LANGUAGE.lower() == 'es':
            video_html = utils.get_webcontent(
                URL_LIVE_ES)
            video_uri = re.compile(
                r'data-mtv-uri="(.*?)"').findall(video_html)[0]
        elif DESIRED_LANGUAGE.lower() == 'it':
            video_html = utils.get_webcontent(
                URL_LIVE_IT)
            video_uri_1 = re.compile(
                r'data-mtv-uri="(.*?)"').findall(video_html)[0]
            headers = {'Content-Type': 'application/json', 'referer': 'http://www.paramountchannel.it/tv/diretta'}
            video_html_2 = utils.get_webcontent(
                URL_LIVE_URI % video_uri_1, specific_headers=headers)
            video_uri_jsonparser = json.loads(video_html_2)
            video_uri = video_uri_jsonparser["feed"]["items"][0]["guid"]
        else:
            return ''
        return resolver.get_mtvnservices_stream(video_uri)
