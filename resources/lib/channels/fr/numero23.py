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
import re
import json

# TODO
# Rework Replay (most category are empty and lot it and miss)
# Get more info Live TV (picture, plot)

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.addon.initialize_gettext()

url_root = 'http://www.numero23.fr/programmes/'

url_info_live_json = 'http://www.numero23.fr/wp-content/cache/n23-direct.json'
# Title, DailyMotion Id (Video)

url_dailymotion_embed = 'http://www.dailymotion.com/embed/video/%s'
# Video_id

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

@common.plugin.cached(common.cache_time)
def list_shows(params):
    shows = []
    if params.next == 'list_shows_1':
        file_path = utils.download_catalog(
            url_root,
            params.channel_name + '.html')
        root_html = open(file_path).read()
        root_soup = bs(root_html, 'html.parser')

        categories_soup = root_soup.find(
            'div',
            class_='content'
        )

        for category in categories_soup.find_all('h2'):
            category_name = category.get_text().encode('utf-8')
            category_hash = common.sp.md5(category_name).hexdigest()

            shows.append({
                'label': category_name,
                'url': common.plugin.get_url(
                    action='channel_entry',
                    category_hash=category_hash,
                    next='list_shows_pgms',
                    window_title=category_name,
                    category_name=category_name,
                )
            })

    elif params.next == 'list_shows_pgms':
        file_path = utils.download_catalog(
            url_root,
            params.channel_name + '.html')
        root_html = open(file_path).read()
        root_soup = bs(root_html, 'html.parser')

        categories_soup = root_soup.find(
            'div',
            class_='content'
        )

        for category in categories_soup.find_all('h2'):
            category_name = category.get_text().encode('utf-8')
            category_hash = common.sp.md5(category_name).hexdigest()

            print category_hash
            print params.category_hash

            if params.category_hash == category_hash:
                programs = category.find_next('div')
                for program in programs.find_all('div', class_='program'):
                    program_name_url = program.find('h3').find('a')
                    program_name = program_name_url.get_text().encode('utf-8')
                    program_url = program_name_url['href'].encode('utf-8')
                    program_img = program.find('img')['src'].encode('utf-8')

                    shows.append({
                        'label': program_name,
                        'thumb': program_img,
                        'url': common.plugin.get_url(
                            action='channel_entry',
                            program_url=program_url,
                            next='list_videos',
                            window_title=program_name,
                            program_name=program_name
                        )
                    })

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

    file_path = utils.download_catalog(
        params.program_url,
        '%s_%s.html' % (params.channel_name, params.program_name)
    )
    program_html = open(file_path).read()
    program_soup = bs(program_html, 'html.parser')

    videos_soup = program_soup.find_all('div', class_='box program')

    if len(videos_soup) == 0:
        videos_soup = program_soup.find_all(
            'div', class_='program sticky video')

    for video in videos_soup:
        video_title = video.find(
            'p').get_text().encode('utf-8').replace(
                '\n', ' ').replace('\r', ' ').rstrip('\r\n')
        video_img = video.find('img')['src'].encode('utf-8')
        video_url = video.find('a')['href'].encode('utf-8')

        info = {
            'video': {
                'title': video_title,
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
            'url': common.plugin.get_url(
                action='channel_entry',
                next='play',
                video_url=video_url
            ),
            'is_playable': True,
            'info': info,
            'context_menu': context_menu  #  A ne pas oublier pour ajouter le bouton "Download" à chaque vidéo
        })

    return common.plugin.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE
        ),
        content='tvshows')

#@common.plugin.cached(common.cache_time)
def list_live(params):
    
    lives = []
    
    title = ''
    plot = ''
    duration = 0
    img = ''
    url_live = ''
    
    file_path = utils.download_catalog(
        url_info_live_json,
        '%s_info_live.json' % (params.channel_name)
    )
    file_info_live = open(file_path).read()
    json_parser = json.loads(file_info_live)
        
    title = json_parser["titre"].encode('utf-8')
    
    video_id = json_parser["video"].encode('utf-8')
    
    url_live = url_dailymotion_embed % video_id
    
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

@common.plugin.cached(common.cache_time)
def get_video_url(params):
    
    if params.next == 'play_r':
	video_html = utils.get_webcontent(
	    params.video_url
	)
	video_soup = bs(video_html, 'html.parser')
	video_id = video_soup.find(
	    'div', class_='video')['data-video-id'].encode('utf-8')

	url_daily = url_dailymotion_embed % video_id

	html_daily = utils.get_webcontent(
	    url_daily,)
	
	if params.next == 'download_video':
	    return url_daily
	else:
	    html_daily = html_daily.replace('\\', '')

	    urls_mp4 = re.compile(
		r'{"type":"video/mp4","url":"(.*?)"}],"(.*?)"').findall(html_daily)

	    url_sd = ""
	    url_hd = ""
	    url_hdplus = ""
	    url_default = ""

	    for url, quality in urls_mp4:
		if quality == '480':
		    url_sd = url
		elif quality == '720':
		    url_hd = url
		elif quality == '1080':
		    url_hdplus = url
		url_default = url

	    desired_quality = common.plugin.get_setting('quality')

	    if (desired_quality == 'BEST' or desired_quality == 'DIALOG') and url_hdplus:
		return url_hdplus
	    else:
		return url_default

    elif params.next == 'play_l':
		
	html_live = utils.get_webcontent(params.url)
	html_live = html_live.replace('\\', '')

	url_live = re.compile(r'{"type":"application/x-mpegURL","url":"(.*?)"}]}').findall(html_live)
	
	# Just one flux no quality to choose
	return url_live[0]
