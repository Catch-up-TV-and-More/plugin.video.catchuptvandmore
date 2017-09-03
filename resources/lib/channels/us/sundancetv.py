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

from resources.lib import utils
from resources.lib import common
from bs4 import BeautifulSoup as bs
import re

# TODO
# Add Live TV 
# More videos buttons for shorts
# Get url_video_stream or pubId (shows and movies)

url_root = "http://www.sundance.tv"

url_movies = "http://www.sundance.tv/watch-now/movies"

url_shows = "http://www.sundance.tv/watch-now/"

url_shorts = "http://www.sundance.tv/series/shorts-on-sundancetv/video"

url_live_sundance = 'http://www.sundance.tv/watch-now/stream'

url_video_stream = "http://c.brightcove.com/services/mobile/streaming/index/master.m3u8?videoId=%s&pubId=%s"
# videoId, pubId
pubId_movie_show = '3605490453001'

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.addon.initialize_gettext()

def get_policy_key(data_account, data_player):
    file_js = utils.get_webcontent(url_js_policy_key % (data_account, data_player))
    return re.compile('policyKey:"(.+?)"').findall(file_js)[0]

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
    #modes.append({
	#'label' : 'Live TV',
	#'url': common.plugin.get_url(
	    #action='channel_entry',
	    #next='live_cat',
	    #category='%s Live TV' % params.channel_name.upper(),
	    #window_title='%s Live TV' % params.channel_name.upper()
	#),
    #})
    
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

    if params.next == 'list_shows_1':
		
	video_title = 'Movies'
	shows.append({
	    'label': video_title,
	    'url': common.plugin.get_url(
		action='channel_entry',
		next='list_videos_movies',
		    title=video_title,
		    window_title=video_title
		)
	    })
	
	video_title = 'Shorts'
	shows.append({
	    'label': video_title,
	    'url': common.plugin.get_url(
		action='channel_entry',
		next='list_videos_shorts',
		    title=video_title,
		    window_title=video_title
		)
	    })
	
	video_title = 'Shows'
	shows.append({
	    'label': video_title,
	    'url': common.plugin.get_url(
		action='channel_entry',
		next='list_shows_2',
		    title=video_title,
		    window_title=video_title
		)
	    })
    
    elif params.next == 'list_shows_2':
	file_path = utils.download_catalog(
	    url_shows,
	    '%s_replay_shows.html' % (params.channel_name))
	replay_shows_html = open(file_path).read()
	
	replay_shows_soup = bs(replay_shows_html, 'html.parser')
	datas_shows_soup = replay_shows_soup.find_all('div', class_='listings')
	
	for show in datas_shows_soup:
	    
	    show_title = show.find('a').find('div').get_text().encode('utf-8')
	    show_img = show.find('div', class_='poster').find('a').find('img').get('src')
	    show_url = url_shows + show.find_all('a', class_='episode')[0].get('href').split('/')[2]
	
	    shows.append({
		'label': show_title,
		'thumb': show_img,
		'url': common.plugin.get_url(
		    action='channel_entry',
		    next='list_videos_show',
			title=show_title,
			show_url=show_url,
			window_title=show_title
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
    
    if params.next == 'list_videos_movies':
	file_path = utils.download_catalog(
	    url_movies,
	    '%s_replay_movies.html' % (params.channel_name))
	replay_movies_html = open(file_path).read()
	    
	replay_movies_soup = bs(replay_movies_html, 'html.parser')
	url_movies_soup = replay_movies_soup.find('div', class_='listings')
	
	list_movies = url_movies_soup.find_all('a')
	
	for movie in list_movies:
	    
	    url_movie = url_root + movie.get('href')
	    movie_id = ''
	    movie_id = re.compile(r'\/watch-now\/movie\/(.*?)\/').findall(movie.get('href'))[0]
	    
	    file_path_movie = utils.download_catalog(
		url_movie,
		'%s_replay_%s.html' % (params.channel_name,movie_id))
	    replay_movie_html = open(file_path_movie).read()
	    
	    replay_movie_soup = bs(replay_movie_html, 'html.parser')
	    datas_movie_soup = replay_movie_soup.find('div', class_='video-page-tout')
		    
	    video_title = datas_movie_soup.find('a').find('div', class_='video-player-right').find('h4').get_text().strip().encode('utf-8')
	    video_plot = datas_movie_soup.find('a').find('div', class_='video-player-right').find('p', class_='video-aired').get_text().strip().encode('utf-8') \
			 + '\n' + datas_movie_soup.find('a').find('div', class_='video-player-right').find('p', class_='').get_text().strip().encode('utf-8')
	    video_duration = 0
	    video_img = datas_movie_soup.find('a').find('div').find('div').find('img').get('src').encode('utf-8')
	    video_url = url_video_stream % (movie_id, pubId_movie_show)
	    info = {
		'video': {
		    'title': video_title,
		    #'aired': aired,
		    #'date': date,
		    'duration': video_duration,
		    'plot': video_plot,
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
	    
    elif params.next == 'list_videos_shorts':
	file_path = utils.download_catalog(
	    url_shorts,
	    '%s_replay_shorts.html' % (params.channel_name))
	replay_shorts_html = open(file_path).read()
	    
	replay_shorts_soup = bs(replay_shorts_html, 'html.parser')	
	list_shorts = replay_shorts_soup.find_all('div', class_='box box-media-item clearfix ')
	
	for short in list_shorts:
		    
	    video_title = short.find('h3', class_='title').find('a').get_text().strip().encode('utf-8')
	    video_plot = ''
	    video_plot = short.find('a').find('img').get('alt').encode('utf-8')
	    video_duration = 0
	    video_img = ''
	    video_img = short.find('a').find('img').get('src').encode('utf-8')
	    video_url = ''
	    url_short = short.find('a').get('href').encode('utf-8')
	    
	    file_path_short = utils.download_catalog(
		url_short,
		'%s_replay_%s.html' % (params.channel_name,video_title))
	    replay_short_html = open(file_path_short).read()
	    
	    short_videoid = re.compile(r'\&videoId=(.*?)\&').findall(replay_short_html)[0]
	    short_pubid = re.compile(r'\&publisherID=(.*?)\&').findall(replay_short_html)[0]
	    
	    video_url = url_video_stream % (short_videoid,short_pubid)
	    
	    info = {
		'video': {
		    'title': video_title,
		    #'aired': aired,
		    #'date': date,
		    'duration': video_duration,
		    'plot': video_plot,
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
	    
	    # TODO add More Button
    
    elif params.next == 'list_videos_show':
	
	file_path = utils.download_catalog(
	    params.show_url,
	    '%s_replay_%s_episodes.html' % (params.channel_name,params.title))
	replay_show_episodes_html = open(file_path).read()
	
	replay_show_episodes_soup = bs(replay_show_episodes_html, 'html.parser')
	list_episodes = replay_show_episodes_soup.find_all('a', class_='video-link related-triple')
	
	for episode in list_episodes:
	    
	    video_img = ''
	    video_img = episode.find('div').find('img').get('src').encode('utf-8')
	    video_url = ''
	    video_id = episode.get('href').split('/',6)[-2]
	    video_url = url_video_stream % (video_id,pubId_movie_show)
	    
	    video_title = ''
	    video_title = episode.find('div').find('div', class_='video-text').find('div', class_='video-text-play-btn').find('h4').get_text().encode('utf-8')
	    video_duration = 0
	    video_plot = ''
	    video_datas = replay_show_episodes_soup.find(id="video-%s-hover" % video_id)
	    video_plot = video_datas.find('p', class_="video-availability-window").get_text().strip().encode('utf-8') + '\n' + \
			 video_datas.find('p', class_="video-description").get_text().strip().encode('utf-8')
	    
	    info = {
		'video': {
		    'title': video_title,
		    #'aired': aired,
		    #'date': date,
		    'duration': video_duration,
		    'plot': video_plot,
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
    subtitle = ' - '
    plot = ''
    duration = 0
    img = ''
    url_live = ''
    
    title = '%s Live' % (params.channel_name.upper())
        
    # Get URL Live
    file_path = utils.download_catalog(
	url_live_sundance,
	'%s_live.html' % (params.channel_name))
    live_html = open(file_path).read()
    url_live = url_video_stream % re.compile(r'data-video_id="(.*?)"').findall(live_html)[0]
    
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
    if params.next == 'download_video' or params.next == 'play_r':
	return params.video_url
    elif params.next == 'play_l':
	return params.url_live
