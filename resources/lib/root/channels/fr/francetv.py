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

import ast
import json
import time
from resources.lib import utils
from resources.lib import common


'''
Channels:
    * France 2
    * France 3 Nationale
    * France 4
    * France Ô
    * France 5
    * La 1ère
'''


CHANNEL_CATALOG = 'http://pluzz.webservices.francetelevisions.fr/' \
                  'pluzz/liste/type/replay/nb/10000/chaine/%s'

# CHANNEL_CATALOG = 'https://pluzz.webservices.francetelevisions.fr/' \
#                   'mobile/liste/type/replay/chaine/%s/nb/20/debut/%s'
# page inc: 20

SHOW_INFO = 'http://webservices.francetelevisions.fr/tools/' \
            'getInfosOeuvre/v2/?idDiffusion=%s'

LIVE_INFO = 'http://webservices.francetelevisions.fr/tools/' \
            'getInfosOeuvre/v2/?idDiffusion=SIM_%s'

HDFAUTH_URL = 'http://hdfauth.francetv.fr/esi/TA?format=json&url=%s'

URL_IMG = 'http://refonte.webservices.francetelevisions.fr%s'

URL_SEARCH = 'https://pluzz.webservices.francetelevisions.fr/' \
             'mobile/recherche/nb/20/tri/date/requete/%s/debut/%s'

URL_ALPHA = 'https://pluzz.webservices.francetelevisions.fr/' \
            'mobile/liste/type/replay/tri/alpha/sens/%s/nb/100/' \
            'debut/%s/lastof/1'
# sens: asc or desc
# page inc: 100

URL_SEARCH_VIDEOS = 'https://vwdlashufe-dsn.algolia.net/1/indexes/' \
                    'yatta_prod_contents/query'

URL_SEARCH_PROGRAMS = 'https://vwdlashufe-dsn.algolia.net/1/indexes/' \
                      'yatta_prod_taxonomies/query'

URL_YATTA_VIDEO = 'http://api-front.yatta.francetv.fr/' \
                  'standard/publish/contents/%s'
# Param : id_yatta

HEADERS_YATTA = {
    'X-Algolia-API-Key': '80d9c91958fc448dd20042d399ebdf16',
    'X-Algolia-Application-Id': 'VWDLASHUFE'
}


CATEGORIES_DISPLAY = {
    "france2": "France 2",
    "france3": "France 3",
    "france4": "France 4",
    "france5": "France 5",
    "franceo": "France Ô",
    "guadeloupe": "Guadeloupe 1ère",
    "guyane": "Guyane 1ère",
    "martinique": "Martinique 1ère",
    "mayotte": "Mayotte 1ère",
    "nouvellecaledonie": "Nouvelle Calédonie 1ère",
    "polynesie": "Polynésie 1ère",
    "reunion": "Réunion 1ère",
    "saintpierremiquelon": "St-Pierre et Miquelon 1ère",
    "wallisfutuna": "Wallis et Futuna 1ère",
    "sport": "Sport",
    "info": "Info",
    "documentaire": "Documentaire",
    "seriefiction": "Série & fiction",
    "magazine": "Magazine",
    "jeunesse": "Jeunesse",
    "divertissement": "Divertissement",
    "jeu": "Jeu",
    "culture": "Culture"
}


CATEGORIES = {
    'Toutes catégories': 'https://pluzz.webservices.francetelevisions.fr/'
                         'mobile/liste/type/replay/chaine/%s/nb/20/debut/%s',
    'Info': 'https://pluzz.webservices.francetelevisions.fr/'
            'mobile/liste/type/replay/rubrique/info/nb/20/debut/%s',
    'Documentaire': 'https://pluzz.webservices.francetelevisions.fr/'
                    'mobile/liste/type/replay/rubrique/documentaire/'
                    'nb/20/debut/%s',
    'Série & Fiction': 'https://pluzz.webservices.francetelevisions.fr/'
                       'mobile/liste/type/replay/rubrique/seriefiction/nb/'
                       '20/debut/%s',
    'Magazine': 'https://pluzz.webservices.francetelevisions.fr/'
                'mobile/liste/type/replay/rubrique/magazine/nb/20/debut/%s',
    'Culture': 'https://pluzz.webservices.francetelevisions.fr/'
               'mobile/liste/type/replay/rubrique/culture/nb/20/debut/%s',
    'Jeunesse': 'https://pluzz.webservices.francetelevisions.fr/'
                'mobile/liste/type/replay/rubrique/jeunesse/nb/20/debut/%s',
    'Divertissement': 'https://pluzz.webservices.francetelevisions.fr/'
                      'mobile/liste/type/replay/rubrique/divertissement/nb/'
                      '20/debut/%s',
    'Sport': 'https://pluzz.webservices.francetelevisions.fr/'
             'mobile/liste/type/replay/rubrique/sport/nb/20/debut/%s',
    'Jeu': 'https://pluzz.webservices.francetelevisions.fr/'
           'mobile/liste/type/replay/rubrique/jeu/nb/20/debut/%s',
    'Version multilingue (VM)': 'https://pluzz.webservices.'
                                'francetelevisions.fr/'
                                'mobile/liste/filtre/multilingue/type/'
                                'replay/nb/20/debut/%s',
    'Sous-titrés': 'https://pluzz.webservices.francetelevisions.fr/'
                   'mobile/liste/filtre/soustitrage/type/replay/nb/'
                   '20/debut/%s',
    'Audiodescription (AD)': 'https://pluzz.webservices.francetelevisions.fr/'
                             'mobile/liste/filtre/audiodescription/type/replay'
                             '/nb/20/debut/%s',
    'Tous publics': 'https://pluzz.webservices.francetelevisions.fr/'
                    'mobile/liste/type/replay/filtre/touspublics'
                    '/nb/20/debut/%s'
}


def channel_entry(params):
    """Entry function of the module"""
    if 'replay_entry' == params.next:
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


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def change_to_nicer_name(original_name):
    """Convert id name to label name"""
    if original_name in CATEGORIES_DISPLAY:
        return CATEGORIES_DISPLAY[original_name]
    return original_name


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def root(params):
    params['next'] = 'list_shows_root'
    params['module_name'] = params.module_name
    params['module_path'] = params.module_path
    return channel_entry(params)


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []
    if 'previous_listing' in params:
        shows = ast.literal_eval(params['previous_listing'])

    unique_item = dict()

    real_channel = params.channel_name
    if params.channel_name == 'la_1ere':
        real_channel = 'la_1ere_reunion%2C' \
                       'la_1ere_guyane%2C' \
                       'la_1ere_polynesie%2C' \
                       'la_1ere_martinique%2C' \
                       'la_1ere_mayotte%2C' \
                       'la_1ere_nouvellecaledonie%2C' \
                       'la_1ere_guadeloupe%2C' \
                       'la_1ere_wallisetfutuna%2C' \
                       'la_1ere_saintpierreetmiquelon'

    # Level 0
    if params.next == 'list_shows_root':

        json_filepath = utils.download_catalog(
            CHANNEL_CATALOG % (real_channel),
            '%s.json' % (params.channel_name)
        )
        with open(json_filepath) as json_file:
            json_parser = json.load(json_file)

        emissions = json_parser['reponse']['emissions']
        for emission in emissions:
            rubrique = emission['rubrique'].encode('utf-8')
            if rubrique not in unique_item:
                unique_item[rubrique] = rubrique
                rubrique_title = change_to_nicer_name(rubrique)

                shows.append({
                    'label': rubrique_title,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        rubrique=rubrique,
                        next='list_shows_2_cat',
                        window_title=rubrique_title
                    )
                })

        # Last videos
        shows.append({
            'label': common.GETTEXT('Last videos'),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='list_shows_last',
                page='0',
                window_title=common.GETTEXT('Last videos')
            )
        })

        # Search videos
        shows.append({
            'label': common.GETTEXT('Search videos'),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='search',
                window_title=common.GETTEXT('Search videos'),
                is_folder=False
            )
        })

        # from A to Z
        shows.append({
            'label': common.GETTEXT('From A to Z'),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='list_shows_from_a_to_z',
                window_title=common.GETTEXT('From A to Z')
            )
        })

    # level 1
    elif 'list_shows_from_a_to_z' in params.next:
        shows.append({
            'label': common.GETTEXT('Ascending'),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='list_shows_2_from_a_to_z_CATEGORIES',
                page='0',
                url=URL_ALPHA % ('asc', '%s'),
                sens='asc',
                window_title=params.window_title
            )
        })
        shows.append({
            'label': common.GETTEXT('Descending'),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                next='list_shows_2_from_a_to_z_CATEGORIES',
                page='0',
                url=URL_ALPHA % ('desc', '%s'),
                sens='desc',
                window_title=params.window_title
            )
        })

    # level 1
    elif 'list_shows_last' in params.next:
        for title, url in CATEGORIES.iteritems():
            if 'Toutes catégories' in title:
                url = url % (params.channel_name, '%s')
            shows.append({
                'label': title,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='list_videos_last',
                    page='0',
                    url=url,
                    title=title,
                    window_title=title
                )
            })

    # level 1 or 2
    elif 'list_shows_2' in params.next:

        if 'list_shows_2_cat' in params.next:
            json_filepath = utils.download_catalog(
                CHANNEL_CATALOG % (real_channel),
                '%s.json' % (params.channel_name)
            )

        elif 'list_shows_2_from_a_to_z_CATEGORIES' in params.next:
            json_filepath = utils.download_catalog(
                URL_ALPHA % (params.sens, params.page),
                '%s_%s_%s_alpha.json' % (
                    params.channel_name,
                    params.sens,
                    params.page
                )
            )

        with open(json_filepath) as json_file:
            json_parser = json.load(json_file)
        emissions = json_parser['reponse']['emissions']
        for emission in emissions:
            rubrique = emission['rubrique'].encode('utf-8')
            chaine_id = emission['chaine_id'].encode('utf-8')
            if ('from_a_to_z' in params.next and
                    chaine_id == params.channel_name) or \
                    rubrique == params.rubrique:
                titre_programme = emission['titre_programme'].encode('utf-8')
                if titre_programme != '':
                    id_programme = emission['id_programme'].encode('utf-8')
                    if id_programme == '':
                        id_programme = emission['id_emission'].encode('utf-8')
                    if id_programme not in unique_item:
                        unique_item[id_programme] = id_programme
                        icon = URL_IMG % (emission['image_large'])
                        genre = emission['genre']
                        accroche_programme = emission['accroche_programme']

                        info = {
                            'video': {
                                'title': titre_programme,
                                'plot': accroche_programme,
                                'genre': genre
                            }
                        }
                        shows.append({
                            'label': titre_programme,
                            'thumb': icon,
                            'fanart': icon,
                            'url': common.PLUGIN.get_url(
                                module_path=params.module_path,
                                module_name=params.module_name,
                                action='replay_entry',
                                next='list_videos_1',
                                id_programme=id_programme,
                                page='0',
                                window_title=titre_programme,
                                fanart=icon
                            ),
                            'info': info
                        })
        if params.next == 'list_shows_2_from_a_to_z_CATEGORIES':
            # More videos...
            shows.append({
                'label': common.ADDON.get_localized_string(30700),
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='list_shows_2_from_a_to_z_CATEGORIES',
                    sens=params.sens,
                    page=str(int(params.page) + 100),
                    window_title=params.window_title,
                    update_listing=True,
                    previous_listing=str(shows)
                )
            })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
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

    if 'search' in params.next:
        url_search = URL_SEARCH_VIDEOS
        body = "{\"params\": \"filters=class:video&page=%s&query=%s\"}" % (
            params.page, params.query)

        result = utils.get_webcontent(
            url_search,
            request_type='post',
            specific_headers=HEADERS_YATTA,
            post_dic=body
        )

        json_d = json.loads(result)
        nb_pages = json_d['nbPages']
        for hit in json_d['hits']:
            label = hit['program']['label']
            title = hit['title']
            headline = hit['headline_title']
            desc = hit['description']
            duration = hit['duration']
            season = hit['season_number']
            episode = hit['episode_number']
            id_yatta = hit['id']
            director = hit['director']
            # producer = hit['producer']
            presenter = hit['presenter']
            casting = hit['casting']
            # characters = hit['characters']
            last_publication_date = hit['dates']['last_publication_date']
            image_400 = hit['image']['formats']['vignette_16x9']['urls']['w:400']
            image_1024 = hit['image']['formats']['vignette_16x9']['urls']['w:1024']

            url_root = 'http://api-front.yatta.francetv.fr'
            image_400 = url_root + image_400
            image_1024 = url_root + image_1024

            title = label + ' - ' + title
            if headline and headline != '':
                desc = headline + '\n' + desc

            if not director:
                director = presenter

            info = {
                'video': {
                    'title': title,
                    'plot': desc,
                    'aired': time.strftime(
                        '%Y-%m-%d', time.localtime(last_publication_date)),
                    'date': time.strftime(
                        '%d.%m.%Y', time.localtime(last_publication_date)),
                    'duration': duration,
                    'year': time.strftime(
                        '%Y', time.localtime(last_publication_date)),
                    'mediatype': 'tvshow',
                    'season': season,
                    'episode': episode,
                    'cast': casting.split(', '),
                    'director': director
                }
            }

            download_video = (
                common.GETTEXT('Download'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='download_video',
                    module_path=params.module_path,
                    module_name=params.module_name,
                    id_yatta=id_yatta) + ')'
            )
            context_menu = []
            context_menu.append(download_video)

            videos.append({
                'label': title,
                'fanart': image_1024,
                'thumb': image_400,
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next='play_r',
                    id_yatta=id_yatta
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu,
                # 'subtitles': 'subtitles'
            })

        if int(params.page) != nb_pages - 1:
            # More videos...
            videos.append({
                'label': common.ADDON.get_localized_string(30700),
                'url': common.PLUGIN.get_url(
                    module_path=params.module_path,
                    module_name=params.module_name,
                    action='replay_entry',
                    next=params.next,
                    query=params.query,
                    page=str(int(params.page) + 1),
                    window_title=params.window_title,
                    update_listing=True,
                    previous_listing=str(videos)
                )
            })

        return common.PLUGIN.create_listing(
            videos,
            sort_methods=(
                common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
                common.sp.xbmcplugin.SORT_METHOD_DATE,
                common.sp.xbmcplugin.SORT_METHOD_DURATION,
                common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
                common.sp.xbmcplugin.SORT_METHOD_EPISODE

            ),
            content='tvshows',
            update_listing='update_listing' in params,
            category=common.get_window_title(params)
        )

    elif 'last' in params.next:
        json_filepath = utils.download_catalog(
            params.url % params.page,
            '%s_%s_%s_last.json' % (
                params.channel_name,
                params.page,
                params.title
            )
        )

    elif 'from_a_to_z' in params.next:
        json_filepath = utils.download_catalog(
            params.url % params.page,
            '%s_%s_%s_last.json' % (
                params.channel_name,
                params.page,
                params.sens
            )
        )

    else:
        json_filepath = utils.download_catalog(
            CHANNEL_CATALOG % params.channel_name,
            '%s.json' % params.channel_name
        )
    with open(json_filepath) as json_file:
        json_parser = json.load(json_file)

    emissions = json_parser['reponse']['emissions']
    for emission in emissions:
        id_programme = emission['id_programme'].encode('utf-8')
        if id_programme == '':
            id_programme = emission['id_emission'].encode('utf-8')
        if 'search' in params.next \
                or 'last' in params.next \
                or 'from_a_to_z' in params.next \
                or id_programme == params.id_programme:
            title = ''
            plot = ''
            duration = 0
            date = ''
            genre = ''
            id_diffusion = emission['id_diffusion']
            chaine_id = emission['chaine_id'].encode('utf-8')

            # If we are in search or alpha or last videos cases,
            # only add channel's shows
            if 'search' in params.next or\
                    'from_a_to_z' in params.next or\
                    'last' in params.next:
                if chaine_id != params.channel_name:
                    continue

            file_prgm = utils.get_webcontent(
                SHOW_INFO % (emission['id_diffusion']))
            if(file_prgm != ''):
                json_parser_show = json.loads(file_prgm)
                if json_parser_show['synopsis']:
                    plot = json_parser_show['synopsis'].encode('utf-8')
                if json_parser_show['diffusion']['date_debut']:
                    date = json_parser_show['diffusion']['date_debut']
                    date = date.encode('utf-8')
                if json_parser_show['real_duration']:
                    duration = int(json_parser_show['real_duration'])
                if json_parser_show['titre']:
                    title = json_parser_show['titre'].encode('utf-8')
                if json_parser_show['sous_titre']:
                    title = ' '.join((
                        title,
                        '- [I]',
                        json_parser_show['sous_titre'].encode('utf-8'),
                        '[/I]'))

                if json_parser_show['genre'] != '':
                    genre = \
                        json_parser_show['genre'].encode('utf-8')

                subtitles = []
                if json_parser_show['subtitles']:
                    subtitles_list = json_parser_show['subtitles']
                    for subtitle in subtitles_list:
                        if subtitle['format'] == 'vtt':
                            subtitles.append(
                                subtitle['url'].encode('utf-8'))

                episode = 0
                if 'episode' in json_parser_show:
                    episode = json_parser_show['episode']

                season = 0
                if 'saison' in json_parser_show:
                    season = json_parser_show['saison']

                cast = []
                director = ''
                personnes = json_parser_show['personnes']
                for personne in personnes:
                    fonctions = ' '.join(
                        x.encode('utf-8') for x in personne['fonctions'])
                    if 'Acteur' in fonctions:
                        cast.append(
                            personne['nom'].encode(
                                'utf-8') + ' ' + personne['prenom'].encode(
                                    'utf-8'))
                    elif 'Réalisateur' in fonctions:
                        director = personne['nom'].encode(
                            'utf-8') + ' ' + \
                            personne['prenom'].encode('utf-8')

                year = int(date[6:10])
                day = date[:2]
                month = date[3:5]
                date = '.'.join((day, month, str(year)))
                aired = '-'.join((str(year), month, day))
                # date: string (%d.%m.%Y / 01.01.2009)
                # aired: string (2008-12-07)

                # image = URL_IMG % (json_parserShow['image'])
                image = json_parser_show['image_secure']

                info = {
                    'video': {
                        'title': title,
                        'plot': plot,
                        'aired': aired,
                        'date': date,
                        'duration': duration,
                        'year': year,
                        'genre': genre,
                        'mediatype': 'tvshow',
                        'season': season,
                        'episode': episode,
                        'cast': cast,
                        'director': director
                    }
                }

                download_video = (
                    common.GETTEXT('Download'),
                    'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                        action='download_video',
                        module_path=params.module_path,
                        module_name=params.module_name,
                        id_diffusion=id_diffusion) + ')'
                )
                context_menu = []
                context_menu.append(download_video)

                videos.append({
                    'label': title,
                    'fanart': image,
                    'thumb': image,
                    'url': common.PLUGIN.get_url(
                        module_path=params.module_path,
                        module_name=params.module_name,
                        action='replay_entry',
                        next='play_r',
                        id_diffusion=id_diffusion
                    ),
                    'is_playable': True,
                    'info': info,
                    'context_menu': context_menu,
                    'subtitles': subtitles
                })

    if 'last' in params.next:
        # More videos...
        videos.append({
            'label': common.ADDON.get_localized_string(30700),
            'url': common.PLUGIN.get_url(
                module_path=params.module_path,
                module_name=params.module_name,
                action='replay_entry',
                url=params.url,
                next=params.next,
                page=str(int(params.page) + 20),
                title=params.title,
                window_title=params.window_title,
                update_listing=True,
                previous_listing=str(videos)
            )
        })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_DATE,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
            common.sp.xbmcplugin.SORT_METHOD_EPISODE

        ),
        content='tvshows',
        update_listing='update_listing' in params,
        category=common.get_window_title(params)
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def start_live_tv_stream(params):
    params['next'] = 'play_l'
    return get_video_url(params)


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_video_url(params):
    """Get video URL and start video player"""

    desired_quality = common.PLUGIN.get_setting('quality')

    if params.next == 'play_r' or params.next == 'download_video':
        if 'id_yatta' in params:
            result = utils.get_webcontent(URL_YATTA_VIDEO % params.id_yatta)
            result = json.loads(result)
            for media in result['content_has_medias']:
                if 'si_id' in media['media']:
                    params['id_diffusion'] = media['media']['si_id']
                    break

        json_parser = json.loads(
            utils.get_webcontent(SHOW_INFO % (params.id_diffusion)))

        url_selected = ''

        if desired_quality == "DIALOG":
            all_datas_videos_quality = []
            all_datas_videos_path = []

            for video in json_parser['videos']:
                if video['format'] == 'hls_v5_os' or \
                        video['format'] == 'm3u8-download':
                    if video['format'] == 'hls_v5_os':
                        all_datas_videos_quality.append("HD")
                    else:
                        all_datas_videos_quality.append("SD")
                    all_datas_videos_path.append(
                        (video['url'], video['drm']))

            seleted_item = common.sp.xbmcgui.Dialog().select(
                common.GETTEXT('Choose video quality'),
                all_datas_videos_quality)

            if seleted_item == -1:
                return None

            url_selected = all_datas_videos_path[seleted_item][0]
            drm = all_datas_videos_path[seleted_item][1]

        elif desired_quality == "BEST":
            for video in json_parser['videos']:
                if video['format'] == 'hls_v5_os':
                    url_selected = video['url']
                    drm = video['drm']
        else:
            for video in json_parser['videos']:
                if video['format'] == 'm3u8-download':
                    url_selected = video['url']
                    drm = video['drm']

        if drm:
            utils.send_notification(
                common.ADDON.get_localized_string(30702))
            return None
        else:
            return url_selected

    elif params.next == 'play_l':

        json_parser = json.loads(utils.get_webcontent(
            LIVE_INFO % (params.channel_name)))

        url_hls_v1 = ''
        url_hls_v5 = ''
        url_hls = ''

        for video in json_parser['videos']:
            if 'format' in video:
                if 'hls_v1_os' in video['format'] and \
                        video['geoblocage'] is not None:
                    url_hls_v1 = video['url']
                if 'hls_v5_os' in video['format'] and \
                        video['geoblocage'] is not None:
                    url_hls_v5 = video['url']
                if 'hls' in video['format']:
                    url_hls = video['url']

        final_url = ''

        # Case France 3 Région
        if url_hls_v1 == '' and url_hls_v5 == '':
            final_url = url_hls
        # Case Jarvis
        if common.sp.xbmc.__version__ == '2.24.0' \
                and url_hls_v1 != '':
            final_url = url_hls_v1
        # Case Krypton, Leia, ...
        if final_url == '' and url_hls_v5 != '':
            final_url = url_hls_v5
        elif final_url == '':
            final_url = url_hls_v1

        json_parser2 = json.loads(
            utils.get_webcontent(HDFAUTH_URL % (final_url)))

        return json_parser2['url']


def search(params):
    keyboard = common.sp.xbmc.Keyboard(
        default='',
        title='',
        hidden=False)
    keyboard.doModal()
    if keyboard.isConfirmed():
        query = keyboard.getText()
        params['page'] = '0'
        params['query'] = query
        params['next'] = 'list_videos_search'
        return list_videos(params)
    else:
        return None
