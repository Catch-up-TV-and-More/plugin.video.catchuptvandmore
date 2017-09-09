# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Original work (C) JUL1EN094, SPM, SylvainCecchetto
    Copyright (C) 2016  SylvainCecchetto

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
import ast

# TODO
# Replay (More Refactoring todo)
# Find API for all channel (JSON) get Replay/Live ?
# Get URL Live FROM SITE
# QUALITY

# URL :

url_root_site = 'http://www.%s.fr/'
# Channel

# Live :
url_live_cplus = 'http://www.canalplus.fr/pid3580-live-tv-clair.html'
url_live_c8 = 'http://www.c8.fr/pid5323-c8-live.html'
url_live_cstar = 'http://www.cstar.fr/pid5322-cstar-live.html'
url_live_cnews = 'http://www.cnews.fr/direct'

# Replay Cplus :
url_replay_cplus_auth = 'http://service.mycanal.fr/authenticate.json/iphone/' \
                        '1.6?highResolution=1&isActivated=0&isAuthenticated=0&paired=0'

url_replay_cplus_categories = 'http://service.mycanal.fr/page/%s/4578.json?' \
                              'cache=60000&nbContent=96'
# Token

# Replay C8 & CStar
url_replay_c8_cstar_root = 'http://lab.canal-plus.pro/web/app_prod.php/api/replay/%s'
# Channel id :
# c8 : 1
# cstar : 2
url_replay_c8_cstar_shows = 'http://lab.canal-plus.pro/web/app_prod.php/api/pfv/list/%s/%s'
# channel_id/show_id
url_replay_c8_cstar_video = 'http://lab.canal-plus.pro/web/app_prod.php/api/pfv/video/%s/%s'
# channel_id/video_id

# Replay CNews
url_replay_cnews = 'http://service.itele.fr/iphone/categorie_news?query='
categories_cnews = {
    'http://service.itele.fr/iphone/topnews': 'La Une',
    url_replay_cnews + 'FRANCE': 'France',
    url_replay_cnews + 'MONDE': 'Monde',
    url_replay_cnews + 'POLITIQUE': 'Politique',
    url_replay_cnews + 'JUSTICE': 'Justice',
    url_replay_cnews + 'ECONOMIE': 'Économie',
    url_replay_cnews + 'SPORT': 'Sport',
    url_replay_cnews + 'CULTURE': 'Culture',
    url_replay_cnews + 'INSOLITE': 'Insolite'
}

# Replay/Live => Parameters Channel, VideoId
url_info_content = 'http://service.canal-plus.com/video/rest/getvideosliees/%s/%s?format=json'

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.addon.initialize_gettext()

def channel_entry(params):
    if 'root' in params.next:
        return root(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'live' in params.next:
        return list_live(params)
    elif 'play' in params.next:
        return get_video_url(params)

def get_token():
    token_json = utils.get_webcontent(url_replay_cplus_auth)
    token_json = json.loads(token_json)
    token = token_json['token']
    return token

def get_channel_id(params):
    if params.channel_name == 'c8':
        return '1'
    elif params.channel_name == 'cstar':
        return '2'
    else:
        return '1'

#@common.plugin.cached(common.cache_time)
def root(params):
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
    # Create categories list
    shows = []

    ################### BEGIN CNEWS ###########################
    if params.next == 'list_shows_1' and params.channel_name == 'cnews':
        for category_url, category_title in categories_cnews.iteritems():
            shows.append({
                'label': category_title,
                'url': common.plugin.get_url(
                    action='channel_entry',
                    category_url=category_url,
                    next='list_videos_cat',
                    title=category_title,
                    window_title=category_title
                )
            })

        shows.append({
            'label': 'Les Émissions',
            'url': common.plugin.get_url(
                action='channel_entry',
                category_url='emissions',
                next='list_shows_emissions',
                title='Les Émissions',
                window_title='Les Émissions'
            )
        })

    elif params.next == 'list_shows_emissions' and params.channel_name == 'cnews':
        shows.append({
            'label': 'À la Une',
            'url': common.plugin.get_url(
                action='channel_entry',
                category_url='http://service.itele.fr/iphone/dernieres_emissions?query=',
                next='list_videos_cat',
                title='À la Une',
                window_title='À la Une'
            )
        })

        shows.append({
            'label': 'Magazines',
            'url': common.plugin.get_url(
                action='channel_entry',
                category_url='http://service.itele.fr/iphone/emissions?query=magazines',
                next='list_videos_cat',
                title='Magazines',
                window_title='Magazines'
            )
        })

        shows.append({
            'label': 'Chroniques',
            'url': common.plugin.get_url(
                action='channel_entry',
                category_url='http://service.itele.fr/iphone/emissions?query=chroniques',
                next='list_videos_cat',
                title='Chroniques',
                window_title='Chroniques'
            )
        })
    ################### END CNEWS ###########################

    ################### BEGIN C8 and CStar ##################
    elif params.next == 'list_shows_1' and (params.channel_name == 'c8' or params.channel_name == 'cstar'):
        file_path = utils.download_catalog(
            url_replay_c8_cstar_root % get_channel_id(params),
            '%s.json' % (params.channel_name))
        file_categories = open(file_path).read()
        json_categories = json.loads(file_categories)

        for categories in json_categories:
            title = categories['title'].encode('utf-8')
            slug = categories['slug'].encode('utf-8')

            shows.append({
                'label': title,
                'url': common.plugin.get_url(
                    action='channel_entry',
                    slug=slug,
                    next='list_shows_2',
                    title=title,
                    window_title=title
                )
            })

    elif params.next == 'list_shows_2' and (params.channel_name == 'c8' or params.channel_name == 'cstar'):
        # Create category's programs list
        file_path = utils.download_catalog(
            url_replay_c8_cstar_root % get_channel_id(params),
            '%s_%s.json' % (params.channel_name, params.slug))
        file_categories = open(file_path).read()
        json_categories = json.loads(file_categories)

        for categories in json_categories:
            if categories['slug'].encode('utf-8') == params.slug:
                for programs in categories['programs']:
                    id = str(programs['id'])
                    title = programs['title'].encode('utf-8')
                    slug = programs['slug'].encode('utf-8')
                    videos_recent = str(programs['videos_recent'])

                    shows.append({
                        'label': title,
                        'url': common.plugin.get_url(
                            action='channel_entry',
                            next='list_videos_cat',
                            id=id,
                            videos_recent=videos_recent,
                            slug=slug,
                            title=title,
                            window_title=title
                        )
                    })
    ################### END C8 and CStar ##################

    ################### BEGIN CANAL + ##################
    elif params.next == 'list_shows_1' and params.channel_name == 'cplus':
        if 'url_page' not in params:
            params.url_page = url_replay_cplus_categories % get_token()
        if 'title' not in params:
            params.title = 'root'
        if 'fanart' in params:
            fanart = params.fanart
        else:
            fanart = ''

        file_path = utils.download_catalog(
            params.url_page,
            '%s_%s_%s.json' % (
                params.channel_name,
                params.title,
                common.sp.md5(params.url_page).hexdigest()))
        file_shows = open(file_path).read()
        shows_json = json.loads(file_shows)
        if 'strates' in shows_json:
            strates = shows_json['strates']
            if len(strates) == 1 and 'textList_like' not in params:
                params['title'] = strates[0]['title'].encode('utf-8')
                params['next'] = 'list_shows_2'
                return list_shows(params)
            elif len(strates) == 2 and 'textList_like' not in params:
                for strate in strates:
                    if strate['type'].encode('utf-8') != 'carrousel':
                        params['title'] = strate['title'].encode('utf-8')
                        params['next'] = 'list_shows_2'
                        return list_shows(params)

            for strate in strates:
                if strate['type'] == 'carrousel':
                    for content in strate['contents']:
                        fanart = content['URLImage'].encode('utf-8')
                # Main categories e.g. Séries, Humour, Sport
                if 'textList_like' in params and params.textList_like is True:
                    if 'title' in strate and \
                            strate['title'].encode('utf-8') == params.title:
                        for content in strate['contents']:
                            title = content['title'].encode('utf-8')
                            url_page = content[
                                'onClick']['URLPage'].encode('utf-8')
                            try:
                                subtitle = content['subtitle'].encode('utf-8')
                            except:
                                subtitle = ''
                            try:
                                img = content['URLImage'].encode('utf-8')
                            except:
                                img = ''

                            info = {
                                'video': {
                                    'title': title,
                                    'plot': subtitle,
                                }
                            }

                            shows.append({
                                'label': title,
                                'thumb': img,
                                'url': common.plugin.get_url(
                                    action='channel_entry',
                                    url_page=url_page,
                                    next='list_shows_1',
                                    title=title,
                                    window_title=title,
                                    fanart=fanart
                                ),
                                'info': info
                            })
                else:
                    if strate['type'] == 'textList':
                        for content in strate['contents']:
                            title = content['title'].encode('utf-8')
                            url_page = content[
                                'onClick']['URLPage'].encode('utf-8')
                            try:
                                subtitle = content['subtitle'].encode('utf-8')
                            except:
                                subtitle = ''
                            try:
                                img = content['URLImage'].encode('utf-8')
                            except:
                                img = ''

                            info = {
                                'video': {
                                    'title': title,
                                    'plot': subtitle,
                                }
                            }

                            shows.append({
                                'label': title,
                                'thumb': img,
                                'url': common.plugin.get_url(
                                    action='channel_entry',
                                    url_page=url_page,
                                    next='list_shows_1',
                                    title=title,
                                    window_title=title,
                                    fanart=fanart
                                ),
                                'info': info
                            })
                    # Videos, e.g. "Ne manquez pas"
                    elif strate['type'] == 'contentGrid':
                        title = strate['title'].encode('utf-8')
                        shows.append({
                            'label': title,
                            'url': common.plugin.get_url(
                                action='channel_entry',
                                url_page=params.url_page,
                                next='list_shows_2',
                                title=title,
                                window_title=title,
                            )
                        })
                    # Other levels (subcategories, ...) e.g. "Top emissions"
                    elif strate['type'] == 'contentRow':
                        title = strate['title'].encode('utf-8')
                        shows.append({
                            'label': title,
                            'url': common.plugin.get_url(
                                action='channel_entry',
                                url_page=params.url_page,
                                next='list_shows_2',
                                title=title,
                                window_title=title,
                            )
                        })
        elif 'textList_like' not in params:
            for content in shows_json['contents']:
                title = content['title'].encode('utf-8')
                params['title'] = title
                params['next'] = 'list_shows_2'
                return list_shows(params)

        else:
            for content in shows_json['contents']:
                title = content['title'].encode('utf-8')
                url_page = content[
                    'onClick']['URLPage'].encode('utf-8')
                try:
                    subtitle = content['subtitle'].encode('utf-8')
                except:
                    subtitle = ''
                try:
                    img = content['URLImage'].encode('utf-8')
                except:
                    img = ''

                info = {
                    'video': {
                        'title': title,
                        'plot': subtitle,
                    }
                }

                shows.append({
                    'label': title,
                    'thumb': img,
                    'url': common.plugin.get_url(
                        action='channel_entry',
                        url_page=url_page,
                        next='list_shows_1',
                        title=title,
                        window_title=title,
                        fanart=fanart
                    ),
                    'info': info
                })

    elif params.next == 'list_shows_2' and params.channel_name == 'cplus':
        file_path = utils.download_catalog(
            params.url_page,
            '%s_%s_%s.json' % (
                params.channel_name,
                params.title,
                common.sp.md5(params.url_page).hexdigest()))
        file_shows = open(file_path).read()
        shows_json = json.loads(file_shows)

        if 'strates' in shows_json:
            strates = shows_json['strates']
            for strate in strates:
                if 'title' in strate and \
                        strate['title'].encode('utf-8') == params.title:
                    contents = strate['contents']
        else:
            contents = shows_json['contents']
        for content in contents:
            if 'type' in content and \
                    content['type'].encode('utf-8') == 'quicktime':
                return list_videos(params)
            else:
                params['textList_like'] = True
                params['title'] = params.title
                params['next'] = 'list_shows_1'
                return list_shows(params)

    ################### END CANAL + ##################

    return common.plugin.create_listing(
            shows,
            sort_methods=(
                common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
                common.sp.xbmcplugin.SORT_METHOD_LABEL
            )
        )

#@common.plugin.cached(common.cache_time)
def list_videos(params):
    # Create list video
    videos = []

    ################### BEGIN CNEWS ###########################
    if params.channel_name == 'cnews':
        file_path = utils.download_catalog(
            params.category_url,
            '%s_%s.json' % (params.channel_name, params.title))
        file = open(file_path).read()
        json_category = json.loads(file)

        if 'news' in json_category:
            json_category = json_category['news']
        elif 'videos' in json_category:
            json_category = json_category['videos']
        elif 'topnews' in json_category:
            json_category = json_category['topnews']
        for video in json_category:
            video_id = video['id_pfv'].encode('utf-8')
            category = video['category'].encode('utf-8')
            date_time = video['date'].encode('utf-8')
            # 2017-02-10 22:05:02
            date_time = date_time.split(' ')[0]
            date_splited = date_time.split('-')
            year = date_splited[0]
            mounth = date_splited[1]
            day = date_splited[2]
            aired = '-'.join((year, mounth, day))
            date = '.'.join((day, mounth, year))
            # date : string (%d.%m.%Y / 01.01.2009)
            # aired : string (2008-12-07)
            title = video['title'].encode('utf-8')
            description = video['description'].encode('utf-8')
            thumb = video['preview169'].encode('utf-8')
            video_url = video['video_urlhd'].encode('utf-8')
            if not video_url:
                video_url = 'no_video'

            info = {
                'video': {
                    'title': title,
                    'plot': description,
                    'aired': aired,
                    'date': date,
                    #'duration': duration,
                    'year': year,
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
                    video_urlhd=video_url) + ')'
            )
            context_menu.append(download_video)
            # Fin

            videos.append({
                'label': title,
                'thumb': thumb,
                'url': common.plugin.get_url(
                    action='channel_entry',
                    next='play_r',
                    video_id=video_id,
                    video_urlhd=video_url
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu  #  A ne pas oublier pour ajouter le bouton "Download" à chaque vidéo
            })
    ################### END CNEWS ###########################

    ################### BEGIN C8 and CStar ##################
    elif params.channel_name == 'c8' or params.channel_name == 'cstar':
        file_path = utils.download_catalog(
            url_replay_c8_cstar_shows % (get_channel_id(params), params.videos_recent),
            '%s_%s.json' % (params.channel_name, params.videos_recent))
        file_videos = open(file_path).read()
        videos_json = json.loads(file_videos)

        for video in videos_json:
            id = video['ID'].encode('utf-8')
            try:
                duration = int(video['DURATION'].encode('utf-8'))
            except:
                duration = 0
            description = video['INFOS']['DESCRIPTION'].encode('utf-8')
            views = int(video['INFOS']['NB_VUES'].encode('utf-8'))
            try:
                date_video = video['INFOS']['DIFFUSION']['DATE'].encode('utf-8')  # 31/12/2017
            except:
                date_video = "00/00/0000"
            day = date_video.split('/')[0]
            mounth = date_video.split('/')[1]
            year = date_video.split('/')[2]
            aired = '-'.join((day, mounth, year))
            date = date_video.replace('/', '.')
            title = video['INFOS']['TITRAGE']['TITRE'].encode('utf-8')
            subtitle = video['INFOS']['TITRAGE']['SOUS_TITRE'].encode('utf-8')
            thumb = video['MEDIA']['IMAGES']['GRAND'].encode('utf-8')
            category = video['RUBRIQUAGE']['CATEGORIE'].encode('utf-8')

            if subtitle:
                title = title + ' - [I]' + subtitle + '[/I]'

            info = {
                'video': {
                    'title': title,
                    'plot': description,
                    'aired': aired,
                    'date': date,
                    'duration': duration,
                    'year': year,
                    'genre': category,
                    'playcount': views,
                    'mediatype': 'tvshow'
                }
            }

            # Nouveau pour ajouter le menu pour télécharger la vidéo
            context_menu = []
            download_video = (
                _('Download'),
                'XBMC.RunPlugin(' + common.plugin.get_url(
                    action='download_video',
                    id=id) + ')'
            )
            context_menu.append(download_video)
            # Fin

            videos.append({
                'label': title,
                'thumb': thumb,
                'url': common.plugin.get_url(
                    action='channel_entry',
                    next='play_r',
                    id=id,
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu  #  A ne pas oublier pour ajouter le bouton "Download" à chaque vidéo
            })
    ################### END C8 and CStar ##################

    ################### BEGIN Canal + ##################
    elif params.channel_name == 'cplus':
        if 'previous_listing' in params:
            videos = ast.literal_eval(params['previous_listing'])
        file_path = utils.download_catalog(
            params.url_page,
            '%s_%s_%s.json' % (
                params.channel_name,
                params.title,
                common.sp.md5(params.url_page).hexdigest()))
        file_videos = open(file_path).read()
        videos_json = json.loads(file_videos)
        more_videos = True
        fanart = ''

        if 'strates' in videos_json:
            for strate in videos_json['strates']:
                if strate['type'] == 'carrousel':
                    for content in strate['contents']:
                        fanart = content['URLImage'].encode('utf-8')

                # Check if we are in the correct cotegory
                if 'title' in strate and \
                        strate['title'].encode('utf-8') == params.title:

                    # If we have lot of videos ...
                    if 'URLPage' in strate['paging']:
                        url = strate['paging']['URLPage'].encode('utf-8')
                        url = url + '&indexPage=1'
                        params['url_page'] = url
                        params['fanart'] = fanart
                        return list_videos(params)

                    # Else show only this videos
                    else:
                        for content in strate['contents']:
                            title = content['title'].encode('utf-8')
                            try:
                                subtitle = content['subtitle'].encode('utf-8')
                            except:
                                subtitle = ''
                            img = content['URLImage'].encode('utf-8')
                            url_media = content['onClick']['URLPage'].encode('utf-8')

                            info = {
                                'video': {
                                    'title': title,
                                    'plot': subtitle,
                                    'mediatype': 'tvshow'

                                }
                            }

                            videos.append({
                                'label': title,
                                'thumb': img,
                                'fanart': fanart,
                                'url': common.plugin.get_url(
                                    action='channel_entry',
                                    next='play',
                                    url_media=url_media,
                                    url_page=params.url_page,
                                    title=title
                                ),
                                'info': info,
                                'is_playable': True
                            })
        else:
            if len(videos_json['contents']) == 0:
                more_videos = False
            for content in videos_json['contents']:
                title = content['title'].encode('utf-8')
                try:
                    subtitle = content['subtitle'].encode('utf-8')
                except:
                    subtitle = ''
                img = content['URLImage'].encode('utf-8')
                url_media = content['onClick']['URLPage'].encode('utf-8')

                info = {
                    'video': {
                        'title': title,
                        'plot': subtitle,
                        'mediatype': 'tvshow'

                    }
                }

                # Nouveau pour ajouter le menu pour télécharger la vidéo
                context_menu = []
                download_video = (
                    _('Download'),
                    'XBMC.RunPlugin(' + common.plugin.get_url(
                        action='download_video',
                        url_media=url_media) + ')'
                )
                context_menu.append(download_video)
                # Fin

                videos.append({
                    'label': title,
                    'thumb': img,
                    'fanart': params.fanart,
                    'url': common.plugin.get_url(
                        action='channel_entry',
                        next='play_r',
                        url_media=url_media,
                        title=title,
                        fanart=params.fanart
                    ),
                    'info': info,
                    'is_playable': True,
                    'context_menu': context_menu  #  A ne pas oublier pour ajouter le bouton "Download" à chaque vidéo
                })

            if more_videos is True:
                # More videos...
                current_index_page = int(params.url_page[-1])
                videos.append({
                    'fanart': params.fanart,
                    'label': common.addon.get_localized_string(30100),
                    'url': common.plugin.get_url(
                        action='channel_entry',
                        next='list_videos',
                        title=params.title,
                        url_page=params.url_page[:-1] + str(
                            current_index_page + 1),
                        update_listing=True,
                        previous_listing=str(videos),
                        fanart=params.fanart
                    ),

                })
    ################### END Canal + ##################

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
    plot = ''
    duration = 0
    img = ''
    url_live = ''

    url_live_html = ''
    if params.channel_name == 'cplus':
        url_live_html = url_live_cplus
    elif params.channel_name == 'c8':
        url_live_html = url_live_c8
    elif params.channel_name == 'cstar':
        url_live_html = url_live_cstar
    elif params.channel_name == 'cnews':
        url_live_html = url_live_cnews

    file_path_html = utils.download_catalog(
        url_live_html,
        '%s_live.html' % (params.channel_name)
    )
    html_live = open(file_path_html).read()

    video_id_re = ''

    if params.channel_name == 'cnews':
        video_id_re = re.compile(r'content: \'(.*?)\'').findall(html_live)
    else :
        video_id_re = re.compile(r'\bdata-video="(?P<video_id>[0-9]+)"').findall(html_live)

    channel_name_catalog = ''
    if params.channel_name == 'cplus':
        channel_name_catalog = params.channel_name
    elif params.channel_name == 'c8':
        channel_name_catalog = 'd8'
    elif params.channel_name == 'cstar':
        channel_name_catalog = 'd17'
    elif params.channel_name == 'cnews':
        channel_name_catalog = 'itele'

    file_path_json = utils.download_catalog(
        url_info_content % (channel_name_catalog, video_id_re[0]),
        '%s_%s_live.json' % (channel_name_catalog, video_id_re[0])
    )
    file_live_json = open(file_path_json).read()
    json_parser = json.loads(file_live_json)

    title = json_parser["INFOS"]["TITRAGE"]["TITRE"].encode('utf-8')
    plot = json_parser["INFOS"]["DESCRIPTION"].encode('utf-8')
    img = json_parser["MEDIA"]["IMAGES"]["GRAND"].encode('utf-8')
    url_live = json_parser["MEDIA"]["VIDEOS"]["IPAD"].encode('utf-8')

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

#@common.plugin.cached(common.cache_time)
def get_video_url(params):

    # CNews
    if (params.next == 'play_r' and params.channel_name == 'cnews') or (params.next == 'download_video' and params.channel_name == 'cnews'):
        return params.video_urlhd
    # C8 & CStar
    elif (params.next == 'play_r' and (params.channel_name == 'c8' or params.channel_name == 'cstar')) \
         or (params.next == 'download_video' and (params.channel_name == 'c8' or params.channel_name == 'cstar')):
        file_video = utils.get_webcontent(
            url_replay_c8_cstar_video % (get_channel_id(params), params.id)
        )
        video_json = json.loads(file_video)
        return video_json['main']['MEDIA']['VIDEOS']['HLS'].encode('utf-8')
    # Canal +
    elif (params.next == 'play_r' and params.channel_name == 'cplus') or (params.next == 'download_video' and params.channel_name == 'cplus'):
        file_path = utils.get_webcontent(params.url_media)
        media_json = json.loads(file_path)
        url = media_json['detail']['informations']['VoD']['videoURL'].encode('utf-8')
        return url
    # Live CPlus, C8, CStar and CNews
    elif params.next == 'play_l':
        return params.url
