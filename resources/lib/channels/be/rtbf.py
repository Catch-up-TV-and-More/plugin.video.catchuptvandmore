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

from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common
import ast
import re
import json
import time

# TODO (More Work TODO)
# Add categories 
# Add geoblock (info in JSON)
# Add Quality Mode
# Add return to previous date
# Fix JSON video data null ?

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.addon.initialize_gettext()

url_json_categories = 'https://www.rtbf.be/news/api/menu?site=media'

url_replay = 'https://www.rtbf.be/auvio/replay?channelId=%s'
# channel Id, page

url_json_emissions_by_id = 'https://www.rtbf.be/api/media/video?method=getVideoListByEmissionOrdered&args[]=%s'
# emission_id

url_json_video_by_id = 'https://www.rtbf.be/api/media/video?method=getVideoDetail&args[]=%s'
# video_id

url_root_image_rtbf = 'https://ds1.static.rtbf.be'

url_json_live =	'https://www.rtbf.be/api/partner/generic/live/planninglist?target_site=media&partner_key=%s'
# partener_key

url_root_live = 'https://www.rtbf.be/auvio/direct#/'

channel_filter = {
    'laune': 'La Une',
    'ladeux': 'La Deux',
    'latrois': 'La Trois',
    'lapremiere' : 'La Première',
    'vivacite' : 'Vivacité',
    'musiq3' : 'Musiq 3',
    'classic21' : 'Classic 21',
    'purefm' : 'Pure',
    'tarmac' : 'TARMAC',
    'webcreation' : 'Webcréation'
	
}

channel_id = {
    'laune': '1',
    'ladeux': '2',
    'latrois': '3',
    'lapremiere' : '17',
    'vivacite' : '10',
    'musiq3' : '8',
    'classic21' : '7',
    'purefm' : '9',
    'tarmac' : '34'#,
    #'webcreation' : 'Webcréation'
	
}


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
    else:
        return None

def get_partener_key(params):
    
    file_path_root_live = utils.download_catalog(
	url_root_live,
	'%s_root_live.html' % params.channel_name,
    )
    html_root_live = open(file_path_root_live).read()
    
    list_js_files = re.compile(r'<script type="text\/javascript" src="(.*?)">').findall(html_root_live)
    
    partener_key_value = ''
    i = 0
    
    for js_file in list_js_files:
	# Get partener key
	file_path_js = utils.download_catalog(
	    js_file,
	    '%s_partener_key_%s.js' % (params.channel_name, str(i)),
	)
	partener_key_js = open(file_path_js).read()
	
	partener_key = re.compile('partner_key: \'(.+?)\'').findall(partener_key_js)
	if len(partener_key) > 0:
	    partener_key_value = partener_key[0]
	i = i + 1
    
    return partener_key_value

#@common.plugin.cached(common.cache_time)
def mode_replay_live(params):
    modes = []
    
    # Add Replay 
    modes.append({
	'label' : 'Replay',
	'url': common.plugin.get_url(
	    action='channel_entry',
	    next='list_videos_1',
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
    #if 'previous_listing' in params:
	#shows = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_shows_1':
	
	program_title = 'Toutes les videos'
	
	shows.append({
	    'label': program_title,
	    'url': common.plugin.get_url(
		emission_title=program_title,
		action='channel_entry',
		page_replay='1',
		next='list_videos_1',
		window_title=program_title
	    )
	})

    return common.plugin.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        )#,
        #update_listing='update_listing' in params
    )


#@common.plugin.cached(common.cache_time)
def list_videos(params):
    videos = []
    
    if params.next == 'list_videos_1':
    
	channel_id_value = channel_id[params.channel_name]
	
	file_path = utils.download_catalog(
            url_replay % (channel_id_value),
            '%s_replay_%s.html' % (params.channel_name,channel_id_value))
        programs_html = open(file_path).read()
	
	programs_soup = bs(programs_html, 'html.parser')
	
	if params.channel_name == 'lapremiere':
	    programs = programs_soup.find_all('article', class_="col-xs-12 rtbf-media-li rtbf-media-li--replay ")
	else:
	    programs = programs_soup.find_all('article', class_="col-xs-12 rtbf-media-li rtbf-media-li--replay")
	
	for program in programs:
	
	    data_id = program.find('a').get('href').split('id=')[1]
	    
	    file_path = utils.download_catalog(
		url_json_video_by_id % data_id,
		'%s_%s.json' % (
		    params.channel_name,
		    data_id))
	    videos_json = open(file_path).read()
	    videos_jsonparser = json.loads(videos_json)
	    
	    if videos_jsonparser["data"] is not None:
		video_data = videos_jsonparser["data"]
		if video_data["subtitle"]:
		    title = video_data["title"].encode('utf-8') + ' - ' +  video_data["subtitle"].encode('utf-8')
		else:
		    title = video_data["title"].encode('utf-8')
		img = url_root_image_rtbf + video_data["thumbnail"]["full_medium"]
		url_video = video_data["urlHls"]
		plot = ''
		if video_data["description"]:
		    plot = video_data["description"].encode('utf-8')
		duration = 0
		duration = video_data["durations"]
		    
		value_date = time.strftime('%d %m %Y', time.localtime(video_data["liveFrom"]))
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
			url_video=url_video) + ')'
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
			url_video=url_video
		    ),
		    'is_playable': True,
		    'info': info,
		    'context_menu': context_menu  #  A ne pas oublier pour ajouter le bouton "Download" à chaque vidéo
		})
	
	videos.append({
	    'label': 'Jour précédent',
	    'url': common.plugin.get_url(
		emission_title='Jour précédent',
		action='channel_entry',
		next='list_videos_1',
		window_title='Jour précédent',
		update_listing=True
	    )
	})
    
    return common.plugin.create_listing(
	videos,
	sort_methods=(
	    common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
	    common.sp.xbmcplugin.SORT_METHOD_DATE
	),
	content='tvshows',
        update_listing='update_listing' in params)

def format_hours(date):
    date_list = date.split('T')
    date_hour = date_list[1][:5]
    return date_hour

def format_day(date):
    date_list = date.split('T')
    date_dmy = date_list[0].replace('-','/') 
    return date_dmy
    

#@common.plugin.cached(common.cache_time)
def list_live(params):
    
    lives = []
    
    title = ''
    subtitle = ' - '
    plot = ''
    duration = 0
    img = ''
    url_live = ''
    
    file_path = utils.download_catalog(
	url_json_live % (get_partener_key(params)),
	'%s_live.json' % (params.channel_name))
    live_json = open(file_path).read()
    live_jsonparser = json.loads(live_json)
    
    channel_live_in_process = False
    
    for live in live_jsonparser:
	#check in live for this channel today + print start_date
	if type(live["channel"]) is dict:
	    live_channel = live["channel"]["label"].encode('utf-8')
	    if channel_filter[params.channel_name] in live_channel:
		start_date_value = format_hours(live["start_date"])
		end_date_value = format_hours(live["end_date"])
		day_value = format_day(live["start_date"])
		title = live["title"] + ' - ' + day_value + ' - Periode : ' + start_date_value + ' - ' + end_date_value
		url_live = ''
		if live["url_streaming"]:
		    url_live = live["url_streaming"]["url_hls"]
		plot = live["description"].encode('utf-8')
		img = live["images"]["illustration"]["16x9"]["1248x702"]

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
			url_live=url_live,
		    ),
		    'is_playable': True,
		    'info': info
		})
	else:
	    #add exclusivity of Auvio
	    start_date_value = format_hours(live["start_date"])
	    end_date_value = format_hours(live["end_date"])
	    day_value = format_day(live["start_date"])
	    title = 'Exclu Auvio : ' + live["title"] + ' - ' + day_value + ' - Periode : ' + start_date_value + ' - ' + end_date_value
	    url_live = ''
	    if live["url_streaming"]:
		url_live = live["url_streaming"]["url_hls"]
	    plot = live["description"].encode('utf-8')
	    img = live["images"]["illustration"]["16x9"]["1248x702"]

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
		    url_live=url_live,
		),
		'is_playable': True,
		'info': info
	    })
    
    if len(lives) == 0:
	
	title = 'No Live TV for %s Today' % params.channel_name.upper()
	
	info = {
	    'video': {
		'title': title,
		'plot': plot,
		'duration': duration
	    }
	}
	
	lives.append({
	    'label': title,
	    'url' : common.plugin.get_url(
		action='channel_entry',
		next='play_l',
	    ),
	    'is_playable': False,
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
	return params.url_live
    elif params.next == 'play_r':
	return params.url_video
