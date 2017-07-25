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
# Replay More work todo (collection)

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.addon.initialize_gettext()

url_replay = 'http://www.nrj-play.fr/%s/replay'
# channel_name (nrj12, ...)

url_collection_api = 'http://www.nrj-play.fr/%s/api/getreplaytvcollection'
# channel_name (nrj12, ...)

url_replay_api = 'http://www.nrj-play.fr/%s/api/getreplaytvlist'
# channel_name (nrj12, ...) return HTTP 500

url_all_video = 'http://www.nrj-play.fr/sitemap-videos.xml'
# Utilisation de cette methode - perte des collections 

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
        
    if 'list_shows_1' in params.next:
	
	# Pour avoir toutes les videos 
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
	
    return common.plugin.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE
        ),
    )
        


@common.plugin.cached(common.cache_time)
def list_videos(params):
    videos = []

    if params.state_video == 'Tous les programmes':    
	
	file_path = utils.download_catalog(
	    url_all_video,
	    '%s_all_video.xml' % params.channel_name,
	)
	replay_xml = open(file_path).read()
	    
	xmlElements = ET.XML(replay_xml)
	
	programs = xmlElements.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")
	
	for program in programs:
	
	    url_site = program.findtext("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").encode('utf-8')
	    check_string = '%s/replay/' % params.channel_name
	    if url_site.count(check_string) > 0:
		
		# Title
		title_list = url_site.rsplit('/', 1)
		title = title_list[1]		
		title = title.replace("-", " ").upper()
		
		videos_node = program.findall("{http://www.google.com/schemas/sitemap-video/1.1}video")
		for video_node in videos_node:
		
		    # Duration
		    duration = 0
			
		    # Image
		    img = ''
		    img_node = video_node.find("{http://www.google.com/schemas/sitemap-video/1.1}thumbnail_loc")
		    img = img_node.text
			
		    # Url Video
		    url = ''
		    url_node = video_node.find("{http://www.google.com/schemas/sitemap-video/1.1}content_loc")
		    url = url_node.text
		    
		    # Plot
		    plot = ''
		    plot_node = video_node.find("{http://www.google.com/schemas/sitemap-video/1.1}description")
		    plot = plot_node.text
				
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
