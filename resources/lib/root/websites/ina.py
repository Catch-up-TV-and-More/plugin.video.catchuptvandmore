# -*- coding: utf-8 -*-
'''
    Catch-up TV & More
    Copyright (C) 2018 SylvainCecchetto

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

import ast
import json
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import resolver
from resources.lib import common

# TO DO
# Add Premium Account (purchase an account to test)
# Add last videos

URL_ROOT = 'http://www.ina.fr'

URL_PROGRAMS = URL_ROOT + '/blocs/rubrique_sommaire/196?order=asc&page=%s&nbResults=48&mode=%s&range=Toutes'
# Page, Mode

URL_VIDEOS = URL_ROOT + '/layout/set/ajax/recherche/result?q=%s&autopromote=0&typeBlock=ina_resultat_exalead&s=date_diffusion&sa=0&b=%s&type=Video&r=&hf=48&c=ina_emission'
# Name Program, Nb Video (+ 48)

URL_VIDEOS_SEARCH = URL_ROOT + '/layout/set/ajax/recherche/result?q=%s&autopromote=&b=%s&type=Video&r=&hf=48'
# Query, Nb Video (+ 48)

URL_STREAM = 'https://player.ina.fr/notices/%s'
# VideoId

def website_entry(params):
    """Entry function of the module"""
    if 'root' in params.next:
        return root(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)
    elif 'search' in params.next:
        return search(params)
    return None

CATEGORIES = {
    'Toutes les Emissions': 'classic',
    'Toutes les séries': 'serie'
}

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def root(params):
    """Add modes in the listing"""
    modes = []

    for category_name, category_mode in CATEGORIES.iteritems():
        modes.append({
            'label': category_name,
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='website_entry',
                category_mode=category_mode,
                category_name=category_name,
                page='1',
                next='list_shows_1',
                window_title=category_name
            )
        })
    
    # Search videos
    modes.append({
        'label': common.GETTEXT('Search videos'),
        'url': common.PLUGIN.get_url(
            module_path=params.module_path,
            module_name=params.module_name,
            action='website_entry',
            next='search',
            window_title=common.GETTEXT('Search videos'),
            is_folder=False
        )
    })

    return common.PLUGIN.create_listing(
        modes,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_LABEL,
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []
    if 'previous_listing' in params:
        shows = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_shows_1':
        list_programs_json = utils.get_webcontent(
            URL_PROGRAMS % (params.page, params.category_mode))
        list_programs_jsonparser = json.loads(list_programs_json)
        list_programs_soup = bs(list_programs_jsonparser["html"], 'html.parser')
        list_programs = list_programs_soup.find_all(
            'div', class_='media')

        for program_datas in list_programs:

            program_title = program_datas.find('img').get('alt').encode('utf-8')
            program_image = URL_ROOT + program_datas.find('img').get('src')
            program_url = URL_ROOT + program_datas.find('a').get('href')

            shows.append({
                'label': program_title,
                'thumb': program_image,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='website_entry',
                    next='list_videos_1',
                    nb_videos='0',
                    program_url=program_url,
                    title=program_title,
                    window_title=program_title
                )
            })
    
        # More programs...
        shows.append({
            'label': common.ADDON.get_localized_string(30708),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='website_entry',
                next='list_shows_1',
                page=str(int(params.page) + 1),
                update_listing=True,
                category_mode=params.category_mode,
                previous_listing=str(shows)
            )
        })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        update_listing='update_listing' in params,
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []
    if 'previous_listing' in params:
        videos = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_videos_1':

        replay_episodes_html = utils.get_webcontent(params.program_url)
        program_title = re.compile(
            r'&q=(.*?)&auto').findall(replay_episodes_html)[0]
        replay_episodes_json = utils.get_webcontent(
            URL_VIDEOS % (program_title, params.nb_videos))
        list_episodes_jsonparser = json.loads(replay_episodes_json)
        list_episodes_soup = bs(list_episodes_jsonparser["content"], 'html.parser')
        list_episodes = list_episodes_soup.find_all(
            'div', class_='media zoomarticle afficheNotices')

        for episode in list_episodes:
            if episode.find(
                'div', class_=re.compile("media-inapremium-slide")):
                video_title = '[Ina Premium] ' + episode.find(
                    'img').get('alt').encode('utf-8')
            else:
                video_title = episode.find(
                    'img').get('alt').encode('utf-8')
            video_id = episode.find('a').get('href').split('/')[2]
            video_img = episode.find(
                'img').get('src')
            video_duration_text_datas = episode.find('span', class_='duration').get_text().split(' ')
            video_duration = 0
            for video_duration_datas in video_duration_text_datas:
                if 's' in video_duration_datas:
                    video_duration_datas = video_duration_datas.replace('s', '')
                    video_duration = video_duration + int(video_duration_datas)
                elif 'm' in video_duration_datas:
                    video_duration_datas = video_duration_datas.replace('m', '')
                    video_duration = video_duration + (int(video_duration_datas) * 60)
                elif 'h' in video_duration_datas:
                    video_duration_datas = video_duration_datas.replace('h', '')
                    video_duration = video_duration + (int(video_duration_datas) * 3600)

            
            if episode.find('span', class_='broadcast'):
                video_date = episode.find('span', class_='broadcast').get_text().split('/')
                day = video_date[0]
                mounth = video_date[1]
                year = video_date[2]
            else:
                day = '00'
                mounth = '00'
                year = '0000'
            date = '.'.join((day, mounth, year))
            aired = '-'.join((year, mounth, day))

            info = {
                'video': {
                    'title': video_title,
                    'aired': aired,
                    'date': date,
                    'duration': video_duration,
                    # 'plot': video_plot,
                    'year': year,
                    'mediatype': 'tvshow'
                }
            }

            download_video = (
                common.GETTEXT('Download'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='download_video',
                    module_path=params.module_path,
                    module_name=params.module_name,
                    video_id=video_id) + ')'
            )
            context_menu = []
            context_menu.append(download_video)

            videos.append({
                'label': video_title,
                'thumb': video_img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='website_entry',
                    next='play_r',
                    video_id=video_id
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

        # More videos...
        videos.append({
            'label': '# ' + common.ADDON.get_localized_string(30700),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='website_entry',
                next='list_videos_1',
                program_url=params.program_url,
                nb_videos=str(int(params.nb_videos) + 48),
                update_listing=True,
                previous_listing=str(videos)
            )
        })

    elif params.next == 'list_videos_search':
    
        replay_episodes_json = utils.get_webcontent(
            URL_VIDEOS_SEARCH % (params.query, params.nb_videos))
        list_episodes_jsonparser = json.loads(replay_episodes_json)
        list_episodes_soup = bs(list_episodes_jsonparser["content"], 'html.parser')
        list_episodes = list_episodes_soup.find_all(
            'div', class_='media zoomarticle')

        for episode in list_episodes:
            if episode.find(
                'div', class_=re.compile("media-inapremium-search")):
                video_title = '[Ina Premium] ' + episode.find(
                    'img').get('alt').encode('utf-8')
            else:
                video_title = episode.find(
                    'img').get('alt').encode('utf-8')
            video_id = episode.find('a').get('href').split('/')[2]
            video_img = episode.find(
                'img').get('src')
            video_duration_text_datas = episode.find('span', class_='duration').get_text().split(' ')
            video_duration = 0
            for video_duration_datas in video_duration_text_datas:
                if 's' in video_duration_datas:
                    video_duration_datas = video_duration_datas.replace('s', '')
                    video_duration = video_duration + int(video_duration_datas)
                elif 'm' in video_duration_datas:
                    video_duration_datas = video_duration_datas.replace('m', '')
                    video_duration = video_duration + (int(video_duration_datas) * 60)
                elif 'h' in video_duration_datas:
                    video_duration_datas = video_duration_datas.replace('h', '')
                    video_duration = video_duration + (int(video_duration_datas) * 3600)

            
            if episode.find('span', class_='broadcast'):
                video_date = episode.find('span', class_='broadcast').get_text().split('/')
                day = video_date[0]
                mounth = video_date[1]
                year = video_date[2]
            else:
                day = '00'
                mounth = '00'
                year = '0000'
            date = '.'.join((day, mounth, year))
            aired = '-'.join((year, mounth, day))

            info = {
                'video': {
                    'title': video_title,
                    'aired': aired,
                    'date': date,
                    'duration': video_duration,
                    # 'plot': video_plot,
                    'year': year,
                    'mediatype': 'tvshow'
                }
            }

            download_video = (
                common.GETTEXT('Download'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='download_video',
                    module_path=params.module_path,
                    module_name=params.module_name,
                    video_id=video_id) + ')'
            )
            context_menu = []
            context_menu.append(download_video)

            videos.append({
                'label': video_title,
                'thumb': video_img,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='website_entry',
                    next='play_r',
                    video_id=video_id
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

        # More videos...
        videos.append({
            'label': '# ' + common.ADDON.get_localized_string(30700),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='website_entry',
                next='list_videos_1',
                query=params.query,
                nb_videos=str(int(params.nb_videos) + 48),
                update_listing=True,
                previous_listing=str(videos)
            )
        })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        content='tvshows',
        update_listing='update_listing' in params,
        category=common.get_window_title(params)
    )


def get_video_url(params):
    """Get video URL and start video player"""
    stream_xml = utils.get_webcontent(URL_STREAM % params.video_id)
    stream_url = ''
    xml_elements = ET.XML(stream_xml)
    for item in xml_elements.findall('./channel/item'):
        for child in item:
            if child.tag == '{http://search.yahoo.com/mrss/}content':
                stream_url = child.attrib['url']
    return stream_url

def search(params):
    keyboard = common.sp.xbmc.Keyboard(
        default='',
        title='',
        hidden=False)
    keyboard.doModal()
    if keyboard.isConfirmed():
        query = keyboard.getText()
        params['nb_videos'] = '0'
        params['query'] = query
        params['next'] = 'list_videos_search'
        return list_videos(params)
    else:
        return None