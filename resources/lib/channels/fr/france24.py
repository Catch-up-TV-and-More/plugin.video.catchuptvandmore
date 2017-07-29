# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Original work (C) JUL1EN094, SPM, SylvainCecchetto
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

from resources.lib import utils
from resources.lib import common
import json
from bs4 import BeautifulSoup as bs

# TODO 
# Replay add emissions
# Add info LIVE TV
# Select Language settings not show

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.addon.initialize_gettext()

url_live_site = 'http://www.france24.com/%s/'
# Language

def channel_entry(params):
    if 'mode_replay_live' in params.next:
	return mode_replay_live(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'live' in params.next:
	return list_live(params)
    elif 'play' in params.next:
        return get_video_url(params)

#@common.plugin.cached(common.cache_time)
def mode_replay_live(params):
    modes = []
    
    # Add Replay Desactiver
    if params.channel_name != 'france24':
	modes.append({
	    'label' : 'Replay',
	    'url': common.plugin.get_url(
		action='channel_entry',
		next='list_shows_1',
		category='%s Replay' % params.channel_name.upper(),
		window_title='%s Replay' % params.channel_name.upper()
	    ),
	})
    
    # Add Live 
    modes.append({
	'label' : 'Live TV',
	'url': common.plugin.get_url(
	    action='channel_entry',
	    next='live_cat',
	    category='%s Live TV' % params.channel_name.upper(),
	    window_title='%s Live TV' % params.channel_name.upper()
	),
    })
    
    return common.plugin.create_listing(
        modes,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
    )

#@common.plugin.cached(common.cache_time)
def list_shows(params):
    return None

#@common.plugin.cached(common.cache_time)
def list_videos(params):
    return None
    
#@common.plugin.cached(common.cache_time)
def list_live(params):
    
    lives = []
    
    title = ''
    plot = ''
    duration = 0
    img = ''
    url_live = ''
    
    desired_language = common.plugin.get_setting(
        params.channel_id + '.language')
    
    if desired_language == 'FR':
	title = '%s Français Live' % (params.channel_name.upper())
    elif desired_language == 'EN':
	title = '%s English Live' % (params.channel_name.upper())
    elif desired_language == 'AR':
	title = '%s عربية Live' % (params.channel_name.upper())
    
    url_live = url_live_site % desired_language.lower()
    
    file_path = utils.download_catalog(
        url_live,
        '%s_%s_live.html' % (params.channel_name,desired_language.lower())
    )
    html_live = open(file_path).read()
    root_soup = bs(html_live, 'html.parser')
    
    json_parser = json.loads(root_soup.select_one("script[type=application/json]").text)
    media_datas_list = json_parser['medias']['media']['media_sources']['media_source']
    for datas in media_datas_list:
	if datas['source']:
	    url_live = datas['source']
    
    info = {
	'video': {
	    'title': title,
	    'plot': plot,
	    'duration': duration
	}
    }
    
    lives.append({
	'label': title,
	'fanart': img,
	'thumb': img,
	'url' : common.plugin.get_url(
	    action='channel_entry',
	    next='play_l',
	    url=url_live,
	),
	'is_playable': True,
	'info': info
    })
    
    return common.plugin.create_listing(
	lives,
	sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        )
    )

#@common.plugin.cached(common.cache_time)
def get_video_url(params):
    
    if params.next == 'play_l':
	return params.url

