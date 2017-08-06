# -*- coding: utf-8 -*-
'''
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
'''

import json
import xbmcgui
from resources.lib import utils
from resources.lib import common
import ast
from bs4 import BeautifulSoup as bs


# TODO
# Add Live TV (Done for RMCDecouverte | Todo Other channels)
# RMC DECOUVERTE (Get Policy Key from WebSite)
# Add Download Video

url_token = 'http://api.nextradiotv.com/%s-applications/'
#channel

url_menu = 'http://www.bfmtv.com/static/static-mobile/bfmtv/' \
           'ios-smartphone/v0/configuration.json'

url_replay = 'http://api.nextradiotv.com/%s-applications/%s/' \
             'getPage?pagename=replay'
# channel, token

url_show = 'http://api.nextradiotv.com/%s-applications/%s/' \
           'getVideosList?category=%s&count=100&page=%s'
# channel, token, category, page_number

url_video = 'http://api.nextradiotv.com/%s-applications/%s/' \
            'getVideo?idVideo=%s'
# channel, token, video_id

# RMC Decouverte
url_replay_rmcdecouverte = 'http://rmcdecouverte.bfmtv.com/mediaplayer-replay/'

url_video_html_rmcdecouverte = 'http://rmcdecouverte.bfmtv.com/mediaplayer-replay/?id=%s'
# VideoId_html

url_live_rmcdecouverte = 'http://rmcdecouverte.bfmtv.com/mediaplayer-direct/'

url_video_json_rmcdecouverte = 'https://edge.api.brightcove.com/playback/v1/accounts/%s/videos/%s'
# IdAccount, VideoId

# TODO GET on WebPage
# data-account="1969646226001" data-player="HyW8Pbfyx"
# http://players.brightcove.net/1969646226001/HyW8Pbfyx_default/index.min.js
# "policyKey:" in js file
policy_key = 'BCpkADawqM3-H-cGaUXCjg2IuDbluEd1BT3q086vXDTLVFgA2eMaNF90cjMkry6ebdIkVw6TIyYe1T-krizHY64cZrpBGZeq9AfATMPoQSDwPZysf9srEJaU9rRevqraXlqFQ8eRh5WJ_vG4'

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.addon.initialize_gettext()


@common.plugin.cached(common.cache_time)
def get_token(channel_name):
    file_token = utils.get_webcontent(url_token % (channel_name))
    token_json = json.loads(file_token)
    return token_json['session']['token'].encode('utf-8')


def channel_entry(params):
    if 'mode_replay_live' in params.next:
	return mode_replay_live(params)
    if 'list_shows' in params.next:
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
    if params.channel_name == 'rmcdecouverte':
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
    # Create categories list
    shows = []

    if params.channel_name == 'rmcdecouverte':
	
	if params.next == 'list_shows_1':
	    title = 'Toutes les Vidéos'
	    
	    shows.append({
		'label': title,
		'url': common.plugin.get_url(
		    action='channel_entry',
		    next='list_shows_2',
		    title=title,
		    page='1',
		    window_title=title
		)
	    })
	elif params.next == 'list_shows_2':
	    file_path = utils.download_catalog(
		url_replay_rmcdecouverte,
		'%s_replay.html' % (params.channel_name))
	    program_html = open(file_path).read()
	    
	    program_soup = bs(program_html, 'html.parser')
	    videos_soup = program_soup.find_all('article', class_='art-c modulx2-5 bg-color-rub0-1 box-shadow relative')
	    for video in videos_soup:
		video_id = video.find('figure').find('a')['href'].split('&', 1 )[0].rsplit('=',1)[1]
		video_img = video.find('figure').find('a').find('img')['data-original']
		video_titles = video.find('div', class_="art-body").find('a').find('h2').get_text().encode('utf-8').replace('\n', ' ').replace('\r', ' ').split(' ')
		video_title = ''
		for i in video_titles:
		    video_title = video_title + ' ' + i.strip()
		
		shows.append({
		    'label': video_title,
		    'thumb': video_img,
		    'url': common.plugin.get_url(
			action='channel_entry',
			next='list_videos_1',
			video_id = video_id,
			title=video_title,
			page='2',
			window_title=video_title
		    )
		})
		
    else:
	if params.next == 'list_shows_1':
	    file_path = utils.download_catalog(
		url_replay % (params.channel_name, get_token(params.channel_name)),
		'%s.json' % (params.channel_name))
	    file_categories = open(file_path).read()
	    json_categories = json.loads(file_categories)
	    json_categories = json_categories['page']['contents'][0]
	    json_categories = json_categories['elements'][0]['items']

	    for categories in json_categories:
		title = categories['title'].encode('utf-8')
		image_url = categories['image_url'].encode('utf-8')
		category = categories['categories'].encode('utf-8')

		shows.append({
		    'label': title,
		    'thumb': image_url,
		    'url': common.plugin.get_url(
			action='channel_entry',
			category=category,
			next='list_videos_1',
			title=title,
			page='1',
			window_title=title
		    )
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
    
    if params.channel_name == 'rmcdecouverte':
	file_path = utils.download_catalog(
	    url_video_html_rmcdecouverte % (params.video_id),
	    '%s_%s_replay.html' % (params.channel_name,params.video_id))
	video_html = open(file_path).read()
	    
	video_soup = bs(video_html, 'html.parser')
	data_video_soup = video_soup.find('div', class_='next-player')
	
	data_account = data_video_soup['data-account']
	data_video_id = data_video_soup['data-video-id']
	
	# Method to get JSON from 'edge.api.brightcove.com'
	file_json = utils.download_catalog(
	    url_video_json_rmcdecouverte % (data_account,data_video_id),
	    '%s_%s_replay.json' % (data_account,data_video_id),
	    force_dl=False,
	    request_type='get',
	    post_dic={},
	    random_ua=False,
	    specific_headers={'Accept': 'application/json;pk=%s' % policy_key},
	    params={})
	video_json = open(file_json).read()
	json_parser = json.loads(video_json)
	
	
	video_title = ''
	program_title = ''
	for program in json_parser["tags"]:
	    program_title = program.upper() + ' - '
	video_title = program_title + json_parser["name"].encode('utf-8').lower()
	video_img = ''
	for poster in json_parser["poster_sources"]:
	    video_img = poster["src"]
	video_plot = json_parser["long_description"].encode('utf-8')
	video_duration = 0
	video_duration = json_parser["duration"] / 1000
	video_url = ''
	for url in json_parser["sources"]:
	    if 'type' in url:
		video_url = url["src"].encode('utf-8')
		
	date_value_list = json_parser["published_at"].split('T')[0].split('-')
	
	day = date_value_list[2]
	mounth = date_value_list[1]
	year = date_value_list[0]

	date = '.'.join((day, mounth, year))
	aired = '-'.join((year, mounth, day))

	info = {
	    'video': {
		'title': video_title,
		'aired': aired,
		'date': date,
		'duration': video_duration,
		'plot': video_plot,
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
		video_url=video_url) + ')'
	)
	context_menu.append(download_video)
	# Fin

	videos.append({
	    'label': video_title,
	    'thumb': video_img,
	    'fanart': video_img,
	    'url': common.plugin.get_url(
		action='channel_entry',
		next='play_r',
		video_url=video_url
	    ),
	    'is_playable': True,
	    'info': info,
	    'context_menu': context_menu  #  A ne pas oublier pour ajouter le bouton "Download" à chaque vidéo
	})
		
    else:
	if 'previous_listing' in params:
	    videos = ast.literal_eval(params['previous_listing'])

	if params.next == 'list_videos_1':
	    file_path = utils.download_catalog(
		url_show % (
		    params.channel_name, 
		    get_token(params.channel_name),
		    params.category,
		    params.page),
		'%s_%s_%s.json' % (
		    params.channel_name,
		    params.category,
		    params.page))
	    file_show = open(file_path).read()
	    json_show = json.loads(file_show)

	    for video in json_show['videos']:
		video_id = video['video'].encode('utf-8')
		video_id_ext = video['id_ext'].encode('utf-8')
		category = video['category'].encode('utf-8')
		title = video['title'].encode('utf-8')
		description = video['description'].encode('utf-8')
		begin_date = video['begin_date'] # 1486725600,
		image = video['image'].encode('utf-8')
		duration = video['video_duration_ms'] / 1000

		info = {
		    'video': {
			'title': title,
			'plot': description,
			#'aired': aired,
			#'date': date,
			'duration': duration,
			#'year': year,
			'genre': category,
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
		    'thumb': image,
		    'url': common.plugin.get_url(
			action='channel_entry',
			next='play',
			video_id=video_id,
			video_id_ext=video_id_ext
		    ),
		    'is_playable': True,
		    'info': info,
		    'context_menu': context_menu  #  A ne pas oublier pour ajouter le bouton "Download" à chaque vidéo
		})

	    # More videos...
	    videos.append({
		'label': common.addon.get_localized_string(30100),
		'url': common.plugin.get_url(
		    action='channel_entry',
		    category=params.category,
		    next='list_videos_1',
		    title=title,
		    page=str(int(params.page) + 1),
		    window_title=params.window_title,
		    update_listing=True,
		    previous_listing=str(videos)
		)

	    })

    return common.plugin.create_listing(
	videos,
	sort_methods=(
	    common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
	    common.sp.xbmcplugin.SORT_METHOD_DURATION,
	    common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
	    common.sp.xbmcplugin.SORT_METHOD_GENRE,
	    common.sp.xbmcplugin.SORT_METHOD_UNSORTED
	),
	content='tvshows',
	update_listing='update_listing' in params,
    )

#@common.plugin.cached(common.cache_time)
def list_live(params):
    
    lives = []
    
    title = ''
    plot = ''
    duration = 0
    img = ''
    url_live = ''
    
    if params.channel_name == 'rmcdecouverte':
	
	file_path = utils.download_catalog(
	    url_live_rmcdecouverte,
	    '%s_live.html' % (params.channel_name))
	live_html = open(file_path).read()
	    
	live_soup = bs(live_html, 'html.parser')
	data_live_soup = live_soup.find('div', class_='next-player')
	
	data_account = data_live_soup['data-account']
	data_video_id = data_live_soup['data-video-id']
	
	# Method to get JSON from 'edge.api.brightcove.com'
	file_json = utils.download_catalog(
	    url_video_json_rmcdecouverte % (data_account,data_video_id),
	    '%s_%s_live.json' % (data_account,data_video_id),
	    force_dl=False,
	    request_type='get',
	    post_dic={},
	    random_ua=False,
	    specific_headers={'Accept': 'application/json;pk=%s' % policy_key},
	    params={})
	video_json = open(file_json).read()
	json_parser = json.loads(video_json)
    
	title = json_parser["name"]
	plot = json_parser["long_description"].encode('utf-8')
	
	for url in json_parser["sources"]:
	    url_live = url["src"].encode('utf-8')
	
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
		video_url=url_live,
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
    if params.channel_name == 'rmcdecouverte':
	return params.video_url
    else:
	file_medias = utils.get_webcontent(
	    url_video % (params.channel_name, get_token(params.channel_name), params.video_id))
	json_parser = json.loads(file_medias)

	video_streams = json_parser['video']['medias']
	    
	desired_quality = common.plugin.get_setting('quality')
	    
	if desired_quality == "DIALOG":
	    all_datas_videos = []
	    for datas in video_streams:
		new_list_item = xbmcgui.ListItem()
		new_list_item.setLabel("Video Height : " + str(datas['frame_height']) + " (Encoding : " + str(datas['encoding_rate']) + ")")
		new_list_item.setPath(datas['video_url'])
		all_datas_videos.append(new_list_item)
		    
	    seleted_item = xbmcgui.Dialog().select("Choose Stream", all_datas_videos)
		    
	    return all_datas_videos[seleted_item].getPath().encode('utf-8')

	elif desired_quality == 'BEST':
	    #GET LAST NODE (VIDEO BEST QUALITY)
	    url_best_quality = ''
	    for datas in video_streams:
		url_best_quality = datas['video_url'].encode('utf-8')
	    return url_best_quality
	else:
	    #DEFAULT VIDEO
	    return json_parser['video']['video_url'].encode('utf-8')
