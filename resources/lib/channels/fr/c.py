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
import re
import json

# TODO 
# Replay 
# Download Mode
# Find API for all channel (JSON) get Replay/Live ? 
# Get URL Live FROM SITE
# QUALITY TODO

# URL :

url_root_site = 'http://www.%s.fr/'
# Channel 

# Live : 
url_live_cplus = 'http://www.canalplus.fr/pid3580-live-tv-clair.html'
url_live_c8 = 'http://www.c8.fr/pid5323-c8-live.html'
url_live_cstar = 'http://www.cstar.fr/pid5322-cstar-live.html'
url_live_cnews = 'http://www.cnews.fr/direct'

# Replay :
url_replay_cplus = ''
url_replay_c8 = ''
url_replay_cstar = ''
url_replay_cnews = ''

# Replay/Live => Parameters Channel, VideoId
url_info_content = 'http://service.canal-plus.com/video/rest/getVideos/%s/%s?format=json'

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
    
    # Add Replay 
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
    
    url_live_html = ''
    if params.channel_name == 'cplus':
	url_live_html = url_live_cplus
    elif params.channel_name == 'c8':
	url_live_html = url_live_c8
    elif params.channel_name == 'cstar':
	url_live_html = url_live_cstar
    elif params.channel_name == 'cnews':
	url_live_html = url_live_cnews
    
    file_path_html = utils.download_catalog(
        url_live_html,
        '%s_live.html' % (params.channel_name)
    )
    html_live = open(file_path_html).read()
    
    video_id_re = ''
    
    if params.channel_name == 'cnews':
	video_id_re = re.compile(r'content: \'(.*?)\'').findall(html_live)
    else :
	video_id_re = re.compile(r'\bdata-video="(?P<video_id>[0-9]+)"').findall(html_live)
    
    channel_name_catalog = ''
    if params.channel_name == 'cplus':
	channel_name_catalog = params.channel_name
    elif params.channel_name == 'c8':
	channel_name_catalog = 'd8'
    elif params.channel_name == 'cstar':
	channel_name_catalog = 'd17'
    elif params.channel_name == 'cnews':
	channel_name_catalog = 'itele'
    
    file_path_json = utils.download_catalog(
        url_info_content % (channel_name_catalog, video_id_re[0]),
        '%s_%s_live.json' % (channel_name_catalog, video_id_re[0])
    )
    file_live_json = open(file_path_json).read()
    json_parser = json.loads(file_live_json)
    
    title = json_parser["INFOS"]["TITRAGE"]["TITRE"].encode('utf-8')
    plot = json_parser["INFOS"]["DESCRIPTION"].encode('utf-8')    
    img = json_parser["MEDIA"]["IMAGES"]["GRAND"].encode('utf-8')
    url_live = json_parser["MEDIA"]["VIDEOS"]["IPAD"].encode('utf-8')
    
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
	
