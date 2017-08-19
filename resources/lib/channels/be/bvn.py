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

from resources.lib import utils
from resources.lib import common
import re
import json
from bs4 import BeautifulSoup as bs
import time

# TODO
# Info live (title, picture, plot)
# Add More-Button to get all replay

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.addon.initialize_gettext()

url_root = 'https://www.bvn.tv'

#LIVE :
url_live_site = 'https://www.bvn.tv/bvnlive'
# Get Id
json_live = 'https://json.dacast.com/b/%s/%s/%s'
# Id in 3 part
json_live_token = 'https://services.dacast.com/token/i/b/%s/%s/%s'
# Id in 3 part

# REPLAY :
url_token = 'https://ida.omroep.nl/app.php/auth'
url_programs = 'https://www.bvn.tv/programmas'
url_info_replay = 'https://e.omroep.nl/metadata/%s?callback=jsonpCallback%s5910'
# Id Video, time
url_video_replay = 'https://ida.omroep.nl/app.php/%s?adaptive=yes&token=%s'
# Id Video, Token

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
    shows = []
    
    if params.next == 'list_shows_1':
	file_path = utils.download_catalog(
            url_programs,
            '%s_programs.html' % params.channel_name)
        programs_html = open(file_path).read()
        programs_soup = bs(programs_html, 'html.parser')
	
	categories_soup = programs_soup.find(
            'ul',
            class_='program-video-list'
        )

        for category in categories_soup.find_all('a'):
            category_name = category.find('span').get_text().encode('utf-8').replace(
				'\n', ' ').replace('\r', ' ').rstrip('\r\n')
            category_img =  url_root + category.find('img').get('src').encode('utf-8')
	    
	    url_category = url_root + category.get('href').encode('utf-8')

            shows.append({
                'label': category_name,
		'thumb' : category_img,
		'fanart' : category_img,
                'url': common.plugin.get_url(
                    action='channel_entry',
                    next='list_shows_2',
		    url_category=url_category,
                    window_title=category_name,
                    category_name=category_name,
                )
            })
    
	# TODO Add More Button
    
    elif params.next == 'list_shows_2':
	file_path_2 = utils.download_catalog(
            params.url_category,
            '%s_program_list_episodes.html' % params.channel_name)
        episodes_html = open(file_path_2).read()
        episodes_soup = bs(episodes_html, 'html.parser')
	
	shows_soup = episodes_soup.find(
            'div',
            #id_='video-carousel-part0'#,
	    #class_='custom-carousel carousel slide'
	    class_='active item'
	)

        for episode in shows_soup.find_all('a'):
            episode_name = episode.find('img').get('title').encode('utf-8')
            episode_img =  url_root + episode.find('img').get('src').encode('utf-8')
	    	    
	    id_episode_list = episode.get('href').encode('utf-8').rsplit('/')
	    id_episode = id_episode_list[len(id_episode_list)-1]
	    
            shows.append({
                'label': episode_name,
		'thumb' : episode_img,
		'fanart' : episode_img,
                'url': common.plugin.get_url(
                    action='channel_entry',
                    next='list_videos_cat',
		    id_episode=id_episode,
                    window_title=episode_name,
                    episode_name=episode_name,
                )
            })
	
	# TODO Add More Button ?
	# Clean if return ?
	
    return common.plugin.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
    )

#@common.plugin.cached(common.cache_time)
def list_videos(params):
    videos = []
    
    # get token 
    file_path_json_token = utils.download_catalog(
	url_token,
	'%s_replay_token.json' % (params.channel_name))
    replay_json_token = open(file_path_json_token).read()
    replay_jsonparser_token = json.loads(replay_json_token)
    
    token = replay_jsonparser_token["token"]
    
    # get info replay
    file_path_info_replay = utils.download_catalog(
	url_info_replay % (params.id_episode,str(time.time()).replace('.','')),
	'%s_%s_info_replay.js' % (params.channel_name,params.id_episode))
    info_replay_js = open(file_path_info_replay).read()
    info_replay_json = re.compile(r'\((.*?)\)').findall(info_replay_js)[0]
    info_replay_jsonparser = json.loads(info_replay_json)
    
    title = info_replay_jsonparser["titel"].encode('utf-8') + ' ' +  info_replay_jsonparser["aflevering_titel"].encode('utf-8')
    img = info_replay_jsonparser["images"][0]["url"].encode('utf-8')
    
    plot = info_replay_jsonparser["info"].encode('utf-8')
    duration = 0
    duration = int(info_replay_jsonparser["tijdsduur"].split(':')[0]) * 3600 + int(info_replay_jsonparser["tijdsduur"].split(':')[1]) * 60 \
	       + int(info_replay_jsonparser["tijdsduur"].split(':')[2])
		
    value_date = info_replay_jsonparser["gidsdatum"].split('-')
    day = value_date[2]
    mounth = value_date[1]
    year = value_date[0]

    date = '.'.join((day, mounth, year))
    aired = '-'.join((year, mounth, day))
    
    # Get HLS link
    file_path_video_replay = utils.download_catalog(
	url_video_replay % (params.id_episode,token),
	'%s_%s_video_replay.js' % (params.channel_name,params.id_episode))
    video_replay_json = open(file_path_video_replay).read()
    video_replay_jsonparser = json.loads(video_replay_json)
    
    url_json_url_hls = ''
    
    for video in video_replay_jsonparser["items"][0]:
	url_json_url_hls = video["url"].encode('utf-8')
	break
    
    file_path_hls_replay = utils.download_catalog(
	url_json_url_hls + 'jsonpCallback%s5910' % (str(time.time()).replace('.','')),
	'%s_%s_hls_replay.js' % (params.channel_name,params.id_episode))
    hls_replay_js = open(file_path_hls_replay).read()
    hls_replay_json = re.compile(r'\((.*?)\)').findall(hls_replay_js)[0]
    hls_replay_jsonparser = json.loads(hls_replay_json)
    
    url_hls = hls_replay_jsonparser["url"].encode('utf-8')
    
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
	    url_hls=url_hls) + ')'
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
	    url_hls=url_hls
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
    
    file_path = utils.download_catalog(
	url_live_site,
	'%s_live.html' % (params.channel_name))
    live_html = open(file_path).read()
    id_value = re.compile(r'<script id="(.*?)"').findall(live_html)[0].split('_')
    
    #json with hls
    file_path_json = utils.download_catalog(
	json_live % (id_value[0], id_value[1], id_value[2]),
	'%s_live.json' % (params.channel_name))
    live_json = open(file_path_json).read()
    live_jsonparser = json.loads(live_json)
    
    #json with token
    file_path_json_token = utils.download_catalog(
	json_live_token % (id_value[0], id_value[1], id_value[2]),
	'%s_live_token.json' % (params.channel_name))
    live_json_token = open(file_path_json_token).read()
    live_jsonparser_token = json.loads(live_json_token)
    
    url_live = 'http:' + live_jsonparser["hls"].encode('utf-8') + live_jsonparser_token["token"].encode('utf-8')
    
    title = '%s Live' % params.channel_name.upper() 
	
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
    elif params.next == 'play_r' or params.next == 'download_video':
	return params.url_hls
