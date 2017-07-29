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
import ast
import xbmcgui

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.addon.initialize_gettext()

auth = '?auth=1487366549-2688-mbe66p57-9b64a7bdc99718f9fc20facf756f8be9'

dailymotion_url = 'https://www.dailymotion.com/cdn/manifest/video/'

url_root = 'https://www.lequipe.fr'

categories = {
    'https://www.lequipe.fr/lachainelequipe/morevideos/0/': 'Tout',
    'https://www.lequipe.fr/lachainelequipe/morevideos/1/': 'L\'Équipe du soir',
    'https://www.lequipe.fr/lachainelequipe/morevideos/62/': 'L\'Équipe Type',
    'https://www.lequipe.fr/lachainelequipe/morevideos/88/': 'L\'Équipe Enquête',
    'https://www.lequipe.fr/lachainelequipe/morevideos/46/': 'Esprit Bleu'
}

correct_mounth = {
    'JANV.': '01',
    'FÉVR.': '02',
    'MARS.': '03',
    'AVRI': '04',
    'MAI': '05',
    'JUIN': '06',
    'JUIL.': '07',
    'AOÛT': '08',
    'SEPT.': '09',
    'OCTO.': '10',
    'NOVE.': '11',
    'DECE.': '12'
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


@common.plugin.cached(common.cache_time)
def list_shows(params):
    shows = []

    for category_url, category_name in categories.iteritems():

        shows.append({
            'label': category_name,
            'url': common.plugin.get_url(
                action='channel_entry',
                category_url=category_url,
                page='1',
                category_name=category_name,
                next='list_videos',
                window_title=category_name
            )
        })

    return common.plugin.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL))


#@common.plugin.cached(common.cache_time)
def list_videos(params):
    videos = []
    if 'previous_listing' in params:
        videos = ast.literal_eval(params['previous_listing'])


    url = params.category_url + params.page
    file_path = utils.download_catalog(
        url,
        '%s_%s_%s.html' % (
            params.channel_name,
            params.category_name,
            params.page))
    root_html = open(file_path).read()
    root_soup = bs(root_html, 'html.parser')

    category_soup = root_soup.find_all(
        'a',
        class_='colead')

    for program in category_soup:
        url = program['href'].encode('utf-8')

        title = program.find(
            'h2').get_text().encode('utf-8')
        colead__image = program.find(
            'div',
            class_='colead__image')
        img = colead__image.find(
            'img')['data-src'].encode('utf-8')

        views = colead__image.find(
            'span',
            class_='colead__layerText--topright'
        ).get_text().encode('utf-8')

        views = [int(s) for s in views.split() if s.isdigit()]
        views = views[0]

        date = colead__image.find(
            'span',
            class_='colead__layerText--bottomleft'
        ).get_text().encode('utf-8')  # 10 FÉVR. 2017 | 08:20
        date = date.split(' ')
        day = date[0]
        try:
            mounth = correct_mounth[date[1]]
        except:
            mounth = '00'
        year = date[2]

        date = '.'.join((day, mounth, year))
        aired = '-'.join((year, mounth, day))
        # date : string (%d.%m.%Y / 01.01.2009)
        # aired : string (2008-12-07)

        duration_string = colead__image.find(
            'span',
            class_='colead__layerText--bottomright'
        ).get_text().encode('utf-8')
        duration_list = duration_string.split(':')
        duration = int(duration_list[0]) * 60 + int(duration_list[1])

        info = {
            'video': {
                'title': title,
                'playcount': views,
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
		url=url) + ')'
	)
	context_menu.append(download_video)
	# Fin

        videos.append({
            'label': title,
            'thumb': img,
            'url': common.plugin.get_url(
                action='channel_entry',
                next='play',
                url=url
            ),
            'is_playable': True,
            'info': info#,
            #'context_menu': context_menu  #  A ne pas oublier pour ajouter le bouton "Download" à chaque vidéo
        })

    # More videos...
    videos.append({
        'label': common.addon.get_localized_string(30100),
        'url': common.plugin.get_url(
            action='channel_entry',
            category_url=params.category_url,
            category_name=params.category_name,
            next='list_videos',
            page=str(int(params.page) + 1),
            update_listing=True,
            previous_listing=str(videos)
        ),
    })

    return common.plugin.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_PLAYCOUNT,
            common.sp.xbmcplugin.SORT_METHOD_DATE,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE
        ),
        content='tvshows',
        update_listing='update_listing' in params,
    )


#@common.plugin.cached(common.cache_time)
def get_video_url(params):
    url = url_root + params.url
    html_video_equipe = utils.get_webcontent(
        url)

    url_daily = re.compile(
        r'<iframe src="//(.*?)"', re.DOTALL).findall(html_video_equipe)[0]

    url_daily = 'http://' + url_daily

    html_daily = utils.get_webcontent(
        url_daily,)

    html_daily = html_daily.replace('\\', '')

    all_url_video = re.compile(r'"type":"video/mp4","url":"(.*?)"').findall(html_daily)
    
    desired_quality = common.plugin.get_setting('quality')
	
    if desired_quality == "DIALOG":
	all_datas_videos = []
	for datas in all_url_video:
	    new_list_item = xbmcgui.ListItem()
	    datas_quality = re.search('H264-(.+?)/', datas).group(1)
	    new_list_item.setLabel('H264-' + datas_quality)
	    new_list_item.setPath(datas)
	    all_datas_videos.append(new_list_item)
			
	seleted_item = xbmcgui.Dialog().select("Choose Stream", all_datas_videos)
			
	return all_datas_videos[seleted_item].getPath().encode('utf-8')
    elif desired_quality == 'BEST':
	#Last video in the Best
	for datas in all_url_video:
	    url = datas
	return url
    else:
	return all_url_video[0]
