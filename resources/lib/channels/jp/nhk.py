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
import xml.etree.ElementTree as ET
import re
import json
import base64
import time

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.addon.initialize_gettext()

url_root = 'http://www3.nhk.or.jp/'

url_live_nhk = 'http://www3.nhk.or.jp/%s/app/tv/hlslive_tv.xml'
# Channel_Name...

url_commonjs_nhk = 'http://www3.nhk.or.jp/%s/common/js/common.js'
# Channel_Name...

url_live_info_nhk = 'https://api.nhk.or.jp/%s/epg/v6/%s/now.json?apikey=%s'
# Channel_Name, location, apikey ...

url_categories_nhk = 'https://api.nhk.or.jp/%s/vodcatlist/v2/notzero/list.json?apikey=%s'
# Channel_Name, apikey

url_all_vod_nhk = 'https://api.nhk.or.jp/%s/vodesdlist/v1/all/all/all.json?apikey=%s'
# Channel_Name, apikey

url_video_vod = 'https://player.ooyala.com/sas/player_api/v2/authorization/embed_code/%s/%s?device=html5&domain=www3.nhk.or.jp'
# pcode, Videoid

url_get_js_pcode = 'https://www3.nhk.or.jp/%s/common/player/tv/vod/'
# Channel_Name...

location = ['world']

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

def get_pcode(params):
    # Get js file
    file_path = utils.download_catalog(
	url_get_js_pcode % params.channel_name,
	'%s_js.html' % params.channel_name,
    )
    file_js = open(file_path).read()
    js_file = re.compile('<script src="\/(.+?)"').findall(file_js)
    
    # Get last JS script
    url_get_pcode = url_root + js_file[len(js_file)-1]
    
    # Get apikey
    file_path_js = utils.download_catalog(
	url_get_pcode,
	'%s_pcode.js' % params.channel_name,
    )
    pcode_js = open(file_path_js).read()
    pcode = re.compile('pcode: "(.+?)"').findall(pcode_js)
    return pcode[0]

def get_api_key(params):
    # Get apikey
    file_path_js = utils.download_catalog(
	url_commonjs_nhk % params.channel_name,
	'%s_info.js' % params.channel_name,
    )
    info_js = open(file_path_js).read()
    
    apikey = re.compile('nw_api_key\|\|"(.+?)"').findall(info_js)
    return apikey[0]

#@common.plugin.cached(common.cache_time)
def mode_replay_live(params):
    modes = []
    
    # Add Replay Desactiver
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
    shows = []
    
    if params.next == 'list_shows_1':
		
	all_video = 'All Videos'
	
	shows.append({
	    'label': all_video,
	    'url': common.plugin.get_url(
		action='channel_entry',
		next='list_videos_cat',
		category_id=0,
		all_video=all_video,
		window_title=all_video
	    ),
	})
	
	file_path = utils.download_catalog(
	    url_categories_nhk % (params.channel_name, get_api_key(params)),
	    '%s_categories.json' % (params.channel_name)
	)
	file_categories = open(file_path).read()
	json_parser = json.loads(file_categories)
	
	for category in json_parser["vod_categories"]:
	    
	    name_category = category["name"].encode('utf-8')
	    category_id = category["category_id"]
	    
	    shows.append({
		'label': name_category,
		'url': common.plugin.get_url(
		    action='channel_entry',
		    next='list_videos_cat',
		    category_id=category_id,
		    name_category=name_category,
		    window_title=name_category
		),
	    })
    
    return common.plugin.create_listing(
	shows,
	sort_methods=(
	    common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
	    common.sp.xbmcplugin.SORT_METHOD_LABEL
	)
    )

#@common.plugin.cached(common.cache_time)
def list_videos(params):
    videos = []
    
    if params.next == 'list_videos_cat':
	category_id = params.category_id
	
	file_path = utils.download_catalog(
	    url_all_vod_nhk % (params.channel_name, get_api_key(params)),
	    '%s_all_vod.json' % (params.channel_name)
	)
	file_all_vod = open(file_path).read()
	json_parser = json.loads(file_all_vod)
	
	for episode in json_parser["data"]["episodes"]:
	    
	    episode_to_add = False
	    
	    if str(params.category_id) == '0':
		episode_to_add = True
	    else:
		for category in episode["category"]:
		    if str(category) == str(params.category_id):
			episode_to_add = True
	    
	    if episode_to_add is True:
		title = episode["title_clean"].encode('utf-8') + ' - ' + episode["sub_title_clean"].encode('utf-8')
		img = url_root + episode["image"].encode('utf-8')
		video_id = episode["vod_id"].encode('utf-8')
		plot = episode["description_clean"].encode('utf-8')
		duration = 0
		duration = episode["movie_duration"]
		
		value_date = time.strftime('%d %m %Y', time.localtime(int(str(episode["onair"])[:-3])))
		date = str(value_date).split(' ')
		day = date[0]
		mounth = date[1]
		year = date[2]

		date = '.'.join((day, mounth, year))
		aired = '-'.join((year, mounth, day))
			
		info = {
		    'video': {
			'title': title,
			'plot': plot,
			#'episode': episode_number,
			#'season': season_number,
			#'rating': note,
			'aired': aired,
			'date': date,
			'duration': duration,
			'year': year,
			'mediatype': 'tvshow'
		    }
		}

		# Nouveau pour ajouter le menu pour télécharger la vidéo
		context_menu = []
		download_video = (
		    _('Download'),
		    'XBMC.RunPlugin(' + common.plugin.get_url(
			action='download_video',
			video_id=video_id) + ')'
		)
		context_menu.append(download_video)
		# Fin

		videos.append({
		    'label': title,
		    'thumb': img,
		    'fanart': img,
		    'url': common.plugin.get_url(
			action='channel_entry',
			next='play_r',
			video_id=video_id
		    ),
		    'is_playable': True,
		    'info': info,
		    'context_menu': context_menu  #  A ne pas oublier pour ajouter le bouton "Download" à chaque vidéo
		})
    
    return common.plugin.create_listing(
	videos,
	sort_methods=(
	    common.sp.xbmcplugin.SORT_METHOD_DATE,
	    common.sp.xbmcplugin.SORT_METHOD_DURATION,
	    common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
	    common.sp.xbmcplugin.SORT_METHOD_GENRE,
	    common.sp.xbmcplugin.SORT_METHOD_PLAYCOUNT,
	    common.sp.xbmcplugin.SORT_METHOD_UNSORTED
	),
	content='tvshows')
    
#@common.plugin.cached(common.cache_time)
def list_live(params):
    
    lives = []
    
    title = ''
    subtitle = ' - '
    plot = ''
    duration = 0
    img = ''
    url_live = ''
    
    title = '%s Live' % (params.channel_name.upper())
        
    # Get URL Live
    file_path = utils.download_catalog(
	url_live_nhk % params.channel_name,
	'%s_live.xml' % params.channel_name,
    )
    live_xml = open(file_path).read()
    xmlElements = ET.XML(live_xml)
    url_live = xmlElements.find("tv_url").findtext("wstrm").encode('utf-8')
    
    #GET Info Live
    # Get JSON
    url_json = url_live_info_nhk % (params.channel_name, location[0], get_api_key(params))
    file_path_json = utils.download_catalog(
	url_json,
	'%s_live.json' % params.channel_name,
    )
    live_json = open(file_path_json).read()
    json_parser = json.loads(live_json)
    
    # Get First Element
    for info_live in json_parser['channel']['item']:
	if info_live["subtitle"] != '':
	    subtitle = subtitle + info_live["subtitle"].encode('utf-8')
	title = info_live["title"].encode('utf-8') + subtitle
	
	start_date = time.strftime('%H:%M', time.localtime(int(str(info_live["pubDate"])[:-3])))
	end_date = time.strftime('%H:%M', time.localtime(int(str(info_live["endDate"])[:-3])))
	plot = start_date + ' - ' + end_date + '\n ' + info_live["description"].encode('utf-8')
	img = url_root + info_live["thumbnail"].encode('utf-8')
	break

    
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
    
    if params.next == 'play_r' or params.next == 'download_video':
	url = ''
	file_path = utils.download_catalog(
	    url_video_vod % (get_pcode(params), params.video_id),
	    '%s_%s_video_vod.json' % (params.channel_name, params.video_id)
	)
	video_vod = open(file_path).read()
	json_parser = json.loads(video_vod)
	
	#Get Value url encodebase64
	for stream in json_parser["authorization_data"][params.video_id]["streams"]:
	    url_base64 = stream["url"]["data"]
	url = base64.standard_b64decode(url_base64)
	return url
    elif params.next == 'play_l':
	return params.url
	
