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

# TODO (More Work TODO)
# Add categories 
# Add Live TV
# Add geoblock (info in JSON)
# Add Quality Mode
# etc ...

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.addon.initialize_gettext()

url_json_categories = 'https://www.rtbf.be/news/api/menu?site=media'

url_json_emissions_by_id = 'https://www.rtbf.be/api/media/video?method=getVideoListByEmissionOrdered&args[]=%s'
# emission_id

url_root_image_rtbf = 'https://ds1.static.rtbf.be'

channel_filter = {
    'laune': 'La Une',
    'ladeux': 'La Deux',
    'latrois': 'La Trois',
    'lapremiere' : 'La Première',
    'vivacite' : 'Vivacité',
    'musiq3' : 'Musiq 3',
    'classic21' : 'Classic 21',
    'purefm' : 'PURE',
    'tarmac' : 'TARMAC'
	
}


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
    # if 'previous_listing' in params:
    #     shows = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_shows_1':
        file_path = utils.download_catalog(
            url_json_categories,
            '%s_categories.json' % params.channel_name)
        categories_json = open(file_path).read()
        categories = json.loads(categories_json)

        for category in categories['item']:
            if category['@attributes']['id'] == 'emission':
                category_title = category[
                    '@attributes']['name'].encode('utf-8')
                category_url = category[
                    '@attributes']['url'].encode('utf-8')
                shows.append({
                    'label': category_title,
                    'url': common.plugin.get_url(
                        category_title=category_title,
                        action='channel_entry',
                        category_url=category_url,
                        next='list_shows_cat',
                        window_title=category_title
                    )
                })

    elif params.next == 'list_shows_cat':
        file_path = utils.download_catalog(
            params.category_url,
            '%s_%s.html' % (
                params.channel_name,
                params.category_title))
        category_html = open(file_path).read()
        category_soup = bs(category_html, 'html.parser')

	emissions_soup = category_soup.find_all('article', class_="rtbf-media-item col-xxs-12 ")
	
	for emission in emissions_soup:
	    
	    channel_emission = emission.find('div', class_="rtbf-media-item__meta-bottom").get_text().encode('utf-8')
	    if channel_filter[params.channel_name] in channel_emission:
	    
		emission_title = emission.find('h4').get_text().encode('utf-8')
		data_id = emission['data-id']
	    
		shows.append({
		    'label': emission_title,
		    'url': common.plugin.get_url(
			emission_title=emission_title,
			action='channel_entry',
			data_id=data_id,
			next='list_videos',
			window_title=emission_title
		    )
		})

    return common.plugin.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        update_listing='update_listing' in params
    )


#@common.plugin.cached(common.cache_time)
def list_videos(params):
    videos = []
    
    file_path = utils.download_catalog(
	url_json_emissions_by_id % params.data_id,
	'%s_%s.json' % (
	    params.channel_name,
	    params.data_id))
    videos_json = open(file_path).read()
    videos_jsonparser = json.loads(videos_json)
    
    all_videos_data =  videos_jsonparser["data"]
    for video_data in all_videos_data:
	
	title = video_data["title"].encode('utf-8')
	img = url_root_image_rtbf + video_data["thumbnail"]["full_medium"]
	url_video = video_data["urlHls"]
	plot = ''
	if video_data["description"]:
	    plot = video_data["description"].encode('utf-8')
	duration = 0
	duration = video_data["durations"]
	
	info = {
	    'video': {
		'title': title,
		'plot': plot,
		#'episode': episode_number,
		#'season': season_number,
		#'rating': note,
		#'aired': aired,
		#'date': date,
		'duration': duration,
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
def get_video_url(params):
    return params.url_video
