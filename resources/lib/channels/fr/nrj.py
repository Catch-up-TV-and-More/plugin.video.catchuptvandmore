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
import xml.etree.ElementTree as ET

# TODO
# FIX DOWNLOAD MODE
# Add LIVE TV (Used Token to work)
# Refactor ALL_VIDEO / VIDEO BY CATEGORIES

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.addon.initialize_gettext()

url_replay = 'http://www.nrj-play.fr/%s/replay'
# channel_name (nrj12, ...)

url_collection_api = 'http://www.nrj-play.fr/%s/api/getreplaytvcollection'
# channel_name (nrj12, ...)

url_replay_api = 'http://www.nrj-play.fr/%s/api/getreplaytvlist'
# channel_name (nrj12, ...)

url_all_video = 'http://www.nrj-play.fr/sitemap-videos.xml'
# Basculer sur ce mode si getreplaytvlist toujours ko ? perte des collections 

url_get_api_live = 'http://www.nrj-play.fr/sitemap.xml'
# NOT_USED in this script (link api, live and more)

url_token = 'https://www.nrj-play.fr/compte/session'
# TODO add account for using Live Direct

url_live = 'http://www.nrj-play.fr/nrj12/direct'

url_root = 'http://www.nrj-play.fr'


def channel_entry(params):
    if 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)
    else:
        return None


#@common.plugin.cached(common.cache_time)
def list_shows(params):
    shows = []
    
    unique_item = dict()

    file_path = utils.download_catalog(
	url_collection_api % params.channel_name,
	'%s_collection.xml' % params.channel_name,
    )
    collection_xml = open(file_path).read()
        
    xmlElements = ET.XML(collection_xml)
    
    if 'list_shows_1' in params.next:
	# Build categories list (Tous les programmes, Séries, ...)
	collections = xmlElements.findall("collection")
	
	# Pour avoir toutes les videos certaines videos ont des categories non presentes dans cette URL 'url_collection_api'
	state_video = 'Tous les programmes'
	
	shows.append({
	    'label': state_video,
	    'url': common.plugin.get_url(
		action='channel_entry',
		state_video=state_video,
		next='list_videos_1',
		#title_category=category_name,
		window_title=state_video
	    )
	})
		
	for collection in collections:
	    
	    category_name = collection.findtext("category").encode('utf-8')
	    if category_name not in unique_item:
		if category_name == '':
		    category_name = 'NO_CATEGORY'
		unique_item[category_name] = category_name
		shows.append({
		    'label': category_name,
		    'url': common.plugin.get_url(
			action='channel_entry',
			category_name=category_name,
			next='list_shows_programs',
			#title_category=category_name,
			window_title=category_name
		    )
		})
	
    elif 'list_shows_programs' in params.next:
	# Build programm list (Tous les programmes, Séries, ...)
	collections = xmlElements.findall("collection")
	
	state_video = 'VIDEOS_BY_CATEGORY'
	
	for collection in collections:
	    if params.category_name == collection.findtext("category").encode('utf-8') \
		or (params.category_name == 'NO_CATEGORY' and collection.findtext("category").encode('utf-8') == ''):
		name_program = collection.findtext("name").encode('utf-8')
		img_program = collection.findtext("picture")
		id_program = collection.get("id")
		
		shows.append({
		    'label': name_program,
		    'thumb': img_program,
		    'url': common.plugin.get_url(
			action='channel_entry',
			next='list_videos_1',
			state_video=state_video,
			id_program=id_program,
			#title_program=name_program,
			window_title=name_program
		    )
		})
    
    return common.plugin.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE
        ),
    )
        


#@common.plugin.cached(common.cache_time)
def list_videos(params):
    videos = []

    file_path = utils.download_catalog(
	url_replay_api % params.channel_name,
	'%s_replay.xml' % params.channel_name,
    )
    replay_xml = open(file_path).read()
        
    xmlElements = ET.XML(replay_xml)
    
    programs = xmlElements.findall("program")
        
    for program in programs:
	if params.state_video == 'Tous les programmes':
	    
	    # Title
	    title = program.findtext("title").encode('utf-8') + " - " + program.findtext("subtitle").encode('utf-8')
	    
	    # Duration
	    duration = 0
	    if program.findtext("duration"):
		try:
		    duration = int(program.findtext("duration"))
		except ValueError:
		    pass      # or whatever
	    
	    # Image
	    img = program.find("photos").findtext("photo")
	    
	    # Url Video
	    url = '' #program.find("offres").find("offre").find("videos").findtext("video)
	    for i in program.find("offres").findall("offre"):
		for j in i.find("videos").findall("video"):
		    url = j.text.encode('utf-8')
	    
	    # Plot
	    plot = ''
	    for i in program.find("stories").findall("story"):
		if int(i.get("maxlength")) == 680:
		    plot= i.text.encode('utf-8')
	    	    
	    info = {
		'video': {
		    'title': title,
		    'plot': plot,
		    'duration': duration,
		    #'aired': aired,
		    #'date': date,
		    #'year': year,
		    'mediatype': 'tvshow'
		}
	    }

	    # Nouveau pour ajouter le menu pour télécharger la vidéo
	    context_menu = []
	    download_video = (
		_('Download'),
		'XBMC.RunPlugin(' + common.plugin.get_url(
		    action='download_video',
		    url_video=url) + ')'
	    )
	    context_menu.append(download_video)
	    # Fin

	    videos.append({
		'label': title,
		'fanart': img,
		'thumb': img,
		'url': common.plugin.get_url(
		    action='channel_entry',
		    next='play',
		    url_video=url
		),
		'is_playable': True,
		'info': info,
		'context_menu': context_menu  #  A ne pas oublier pour ajouter le bouton "Download" à chaque vidéo
	    })
	    
	elif params.id_program == program.get("IDSERIE"):
	    
	    # Title
	    title = program.findtext("title").encode('utf-8') + " - " + program.findtext("subtitle").encode('utf-8')
	    
	    # Duration
	    duration = 0
	    if program.findtext("duration"):
		try:
		    duration = int(program.findtext("duration"))
		except ValueError:
		    pass      # or whatever
	    
	    # Image
	    img = program.find("photos").findtext("photo")
	    
	    # Url Video
	    url = '' #program.find("offres").find("offre").find("videos").findtext("video)
	    for i in program.find("offres").findall("offre"):
		for j in i.find("videos").findall("video"):
		    url = j.text.encode('utf-8')
	    
	    # Plot
	    plot = ''
	    for i in program.find("stories").findall("story"):
		if int(i.get("maxlength")) == 680:
		    plot= i.text.encode('utf-8')
	    
	    info = {
		'video': {
		    'title': title,
		    'plot': plot,
		    'duration': duration,
		    #'aired': aired,
		    #'date': date,
		    #'year': year,
		    'mediatype': 'tvshow'
		}
	    }

	    # Nouveau pour ajouter le menu pour télécharger la vidéo
	    context_menu = []
	    download_video = (
		_('Download'),
		'XBMC.RunPlugin(' + common.plugin.get_url(
		    action='download_video',
		    url_video=url) + ')'
	    )
	    context_menu.append(download_video)
	    # Fin

	    videos.append({
		'label': title,
		'fanart': img,
		'thumb': img,
		'url': common.plugin.get_url(
		    action='channel_entry',
		    next='play',
		    url_video=url
		),
		'is_playable': True,
		'info': info#,
		#'context_menu': context_menu  #  A ne pas oublier pour ajouter le bouton "Download" à chaque vidéo
	    })
    
    return common.plugin.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_DATE,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE
        ),
        content='tvshows')

@common.plugin.cached(common.cache_time)
def get_video_url(params):
    # Just One format of each video (no need of QUALITY)
    return params.url_video
