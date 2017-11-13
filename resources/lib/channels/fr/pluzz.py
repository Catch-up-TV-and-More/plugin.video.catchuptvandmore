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

# TO DO
# Liste A à Z
# Si FR3 ou FR1 : Régions

import ast
import json
import time
from resources.lib import utils
from resources.lib import common


# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

context_menu = []
context_menu.append(utils.vpn_context_menu_item())

CHANNEL_CATALOG = 'http://pluzz.webservices.francetelevisions.fr/' \
                  'pluzz/liste/type/replay/nb/10000/chaine/%s'

CHANNEL_LIVE = 'http://pluzz.webservices.francetelevisions.fr/' \
               'pluzz/liste/type/live/nb/10000/chaine/%s'

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

URL_FRANCETV_SPORT = 'https://api-sport-events.webservices.' \
                     'francetelevisions.fr/%s'
# RootMode

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

LIVE_LA_1ERE = {
    "guadeloupe": "Guadeloupe 1ère",
    "guyane": "Guyane 1ère",
    "martinique": "Martinique 1ère",
    "mayotte": "Mayotte 1ère",
    "nouvellecaledonie": "Nouvelle Calédonie 1ère",
    "polynesie": "Polynésie 1ère",
    "reunion": "Réunion 1ère",
    "spm": "St-Pierre et Miquelon 1ère",
    "wallis": "Wallis et Futuna 1ère"
}

LIVE_FR3_REGIONS = {
    "alpes": "le direct France 3 ALPES",
    "alsace": "le direct France 3 ALSACE",
    "aquitaine": "le direct France 3 AQUITAINE",
    "auvergne": "le direct France 3 AUVERGNE",
    "basse_normandie": "le direct France 3 BASSE-NORMANDIE",
    "bourgogne": "le direct France 3 BOURGOGNE",
    "bretagne": "le direct France 3 BRETAGNE",
    "centre": "le direct France 3 CENTRE-VAL DE LOIRE",
    "champagne_ardenne": "le direct France 3 CHAMPAGNE-ARDENNE",
    "corse": "le direct France 3 CORSE",
    "cote_dazur": "le direct France 3 COTE D'AZUR",
    "franche_comte": "le direct France 3 FRANCHE-COMTE",
    "haute_normandie": "le direct France 3 HAUTE-NORMANDIE",
    "languedoc_roussillon": "le direct France 3 LANGUEDOC-ROUSSILLON",
    "limousin": "le direct France 3 LIMOUSIN",
    "lorraine": "le direct France 3 GRAND-EST",
    "nord_pas_de_calais": "le direct France 3 NORD-PAS-DE-CALAIS",
    "paris_ile_de_france": "le direct France 3 PARIS-ILE DE FRANCE",
    "pays_de_la_loire": "le direct France 3 PAYS DE LA LOIRE",
    "picardie": "le direct France 3 PICARDIE",
    "poitou_charentes": "le direct France 3 POITOU-CHARENTES",
    "provence_alpes": "le direct France 3 PROVENCE-ALPES",
    "rhone_alpes": "le direct France 3 RHÔNE-ALPES"
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
    """Add Replay and Live in the listing"""
    modes = []

    if params.channel_name == 'francetvsport':
        next_replay = 'list_videos_ftvsport'
    else:
        next_replay = 'list_shows_1'

    # Add Replay
    if params.channel_name != 'franceinfo' and \
            params.channel_name != 'france3regions':
        modes.append({
            'label': 'Replay',
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next=next_replay,
                mode='replay',
                page='1',
                category='%s Replay' % params.channel_name.upper(),
                window_title='%s Replay' % params.channel_name
            ),
            'context_menu': context_menu
        })

    # Add Live
    modes.append({
        'label': _('Live TV'),
        'url': common.PLUGIN.get_url(
            action='channel_entry',
            next='live_cat',
            mode='live',
            category='%s Live TV' % params.channel_name.upper(),
            window_title='%s Live TV' % params.channel_name
        ),
        'context_menu': context_menu
    })

    # Add Videos
    if params.channel_name == 'francetvsport':
        modes.append({
            'label': 'Videos',
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='list_videos_ftvsport',
                mode='videos',
                page='1',
                category='%s Videos' % params.channel_name.upper(),
                window_title='%s Videos' % params.channel_name
            ),
            'context_menu': context_menu
        })

    return common.PLUGIN.create_listing(
        modes,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title()
    )


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
    if params.next == 'list_shows_1':

        url_json = CHANNEL_CATALOG % (real_channel)
        file_path = utils.download_catalog(
            url_json,
            '%s.json' % (
                params.channel_name))
        file_prgm = open(file_path).read()
        json_parser = json.loads(file_prgm)
        emissions = json_parser['reponse']['emissions']
        for emission in emissions:
            rubrique = emission['rubrique'].encode('utf-8')
            if rubrique not in unique_item:
                unique_item[rubrique] = rubrique
                rubrique_title = change_to_nicer_name(rubrique)

                shows.append({
                    'label': rubrique_title,
                    'url': common.PLUGIN.get_url(
                        action='channel_entry',
                        rubrique=rubrique,
                        next='list_shows_2_cat',
                        window_title=rubrique_title
                    ),
                    'context_menu': context_menu
                })

        # Last videos
        shows.append({
            'label': common.ADDON.get_localized_string(30104),
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='list_shows_last',
                page='0',
                window_title=common.ADDON.get_localized_string(30104)
            ),
            'context_menu': context_menu
        })

        # Search
        shows.append({
            'label': common.ADDON.get_localized_string(30103),
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='search',
                page='0',
                window_title=common.ADDON.get_localized_string(30103)
            ),
            'context_menu': context_menu
        })

        # from A to Z
        shows.append({
            'label': common.ADDON.get_localized_string(30105),
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='list_shows_from_a_to_z',
                window_title=common.ADDON.get_localized_string(30105)
            ),
            'context_menu': context_menu
        })

    # level 1
    elif 'list_shows_from_a_to_z' in params.next:
        shows.append({
            'label': common.ADDON.get_localized_string(30106),
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='list_shows_2_from_a_to_z_CATEGORIES',
                page='0',
                url=URL_ALPHA % ('asc', '%s'),
                sens='asc',
                rubrique='no_rubrique',
                window_title=params.window_title
            ),
            'context_menu': context_menu
        })
        shows.append({
            'label': common.ADDON.get_localized_string(30107),
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='list_shows_2_from_a_to_z_CATEGORIES',
                page='0',
                url=URL_ALPHA % ('desc', '%s'),
                sens='desc',
                rubrique='no_rubrique',
                window_title=params.window_title
            ),
            'context_menu': context_menu
        })

    # level 1
    elif 'list_shows_last' in params.next:
        for title, url in CATEGORIES.iteritems():
            if 'Toutes catégories' in title:
                url = url % (params.channel_name, '%s')
            shows.append({
                'label': title,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='list_videos_last',
                    page='0',
                    url=url,
                    title=title,
                    window_title=title
                ),
                'context_menu': context_menu
            })

    # level 1 or 2
    elif 'list_shows_2' in params.next:
        if 'list_shows_2_cat' in params.next:
            url_json = CHANNEL_CATALOG % (real_channel)
            file_path = utils.download_catalog(
                url_json,
                '%s.json' % (
                    params.channel_name))
        elif 'list_shows_2_from_a_to_z_CATEGORIES' in params.next:
            url_json = URL_ALPHA % (params.sens, params.page)
            file_path = utils.download_catalog(
                url_json,
                '%s_%s_%s_alpha.json' % (
                    params.channel_name,
                    params.sens,
                    params.page))

        file_prgm = open(file_path).read()
        json_parser = json.loads(file_prgm)
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
                                action='channel_entry',
                                next='list_videos_1',
                                id_programme=id_programme,
                                search=False,
                                page='0',
                                window_title=titre_programme,
                                fanart=icon
                            ),
                            'info': info,
                            'context_menu': context_menu
                        })
        if params.next == 'list_shows_2_from_a_to_z_CATEGORIES':
            # More videos...
            shows.append({
                'label': common.ADDON.get_localized_string(30100),
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='list_shows_2_from_a_to_z_CATEGORIES',
                    sens=params.sens,
                    page=str(int(params.page) + 100),
                    window_title=params.window_title,
                    rubrique='no_rubrique',
                    update_listing=True,
                    previous_listing=str(shows)
                ),
                'context_menu': context_menu
            })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        update_listing='update_listing' in params,
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []
    if 'previous_listing' in params:
        videos = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_videos_ftvsport':

        list_videos = utils.get_webcontent(
            URL_FRANCETV_SPORT % (params.mode) + \
            '?page=%s' % (params.page))
        list_videos_parserjson = json.loads(list_videos)

        for video in list_videos_parserjson["page"]["flux"]:

            title = video["title"]
            image = video["image"]["large_16_9"]
            duration = int(video["duration"])
            id_diffusion = video["sivideo-id"]

            info = {
                'video': {
                    'title': title,
                    # 'plot': plot,
                    # 'aired': aired,
                    # 'date': date,
                    'duration': duration,
                    # 'year': year,
                }
            }

            download_video = (
                _('Download'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='download_video',
                    id_diffusion=id_diffusion) + ')'
            )
            context_menu = []
            context_menu.append(download_video)
            context_menu.append(utils.vpn_context_menu_item())

            videos.append({
                'label': title,
                'fanart': image,
                'thumb': image,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='play_r',
                    id_diffusion=id_diffusion
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

        # More videos...
        videos.append({
            'label': common.ADDON.get_localized_string(30100),
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                mode=params.mode,
                next=params.next,
                page=str(int(params.page) + 1),
                title=params.title,
                window_title=params.window_title,
                update_listing=True,
                previous_listing=str(videos)
            ),
            'context_menu': context_menu

        })

    else:

        if 'search' in params.next:
            file_path = utils.download_catalog(
                URL_SEARCH % (params.query, params.page),
                '%s_%s_search.json' % (params.channel_name, params.query),
                force_dl=True
            )

        elif 'last' in params.next:
            file_path = utils.download_catalog(
                params.url % params.page,
                '%s_%s_%s_last.json' % (
                    params.channel_name,
                    params.page,
                    params.title)
            )

        elif 'from_a_to_z' in params.next:
            file_path = utils.download_catalog(
                params.url % params.page,
                '%s_%s_%s_last.json' % (
                    params.channel_name,
                    params.page,
                    params.sens)
            )

        else:
            file_path = utils.download_catalog(
                CHANNEL_CATALOG % params.channel_name,
                '%s.json' % params.channel_name
            )
        file_prgm = open(file_path).read()
        json_parser = json.loads(file_prgm)
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
                                'utf-8') + ' ' + personne['prenom'].encode('utf-8')

                    year = int(date[6:10])
                    day = date[:2]
                    month = date[3:5]
                    date = '.'.join((day, month, str(year)))
                    aired = '-'.join((str(year), month, day))
                    # date : string (%d.%m.%Y / 01.01.2009)
                    # aired : string (2008-12-07)

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
                        _('Download'),
                        'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                            action='download_video',
                            id_diffusion=id_diffusion) + ')'
                    )
                    context_menu = []
                    context_menu.append(download_video)
                    context_menu.append(utils.vpn_context_menu_item())

                    videos.append({
                        'label': title,
                        'fanart': image,
                        'thumb': image,
                        'url': common.PLUGIN.get_url(
                            action='channel_entry',
                            next='play_r',
                            id_diffusion=id_diffusion
                        ),
                        'is_playable': True,
                        'info': info,
                        'context_menu': context_menu
                    })

        if 'search' in params.next:
            # More videos...
            videos.append({
                'label': common.ADDON.get_localized_string(30100),
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='list_videos_search',
                    query=params.query,
                    page=str(int(params.page) + 20),
                    window_title=params.window_title,
                    update_listing=True,
                    previous_listing=str(videos)
                ),
                'context_menu': context_menu
            })

        elif 'last' in params.next:
            # More videos...
            videos.append({
                'label': common.ADDON.get_localized_string(30100),
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    url=params.url,
                    next=params.next,
                    page=str(int(params.page) + 20),
                    title=params.title,
                    window_title=params.window_title,
                    update_listing=True,
                    previous_listing=str(videos)
                ),
                'context_menu': context_menu

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
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_live(params):
    """Build live listing"""
    lives = []

    title = ''
    plot = ''
    duration = 0
    date = ''
    genre = ''

    if params.channel_name == 'francetvsport':

        list_lives = utils.get_webcontent(
            URL_FRANCETV_SPORT % 'directs')
        list_lives_parserjson = json.loads(list_lives)

        if 'lives' in list_lives_parserjson["page"]:

            for live in list_lives_parserjson["page"]["lives"]:
                title = live["title"]
                image = live["image"]["large_16_9"]
                id_diffusion = live["sivideo-id"]

                try:
                    value_date = time.strftime(
                        '%d/%m/%Y %H:%M', time.localtime(live["start"]))
                except Exception:
                    value_date = ''
                plot = 'Live start at ' + value_date

                info = {
                    'video': {
                        'title': title,
                        'plot': plot,
                        # 'aired': aired,
                        # 'date': date,
                        'duration': duration,
                        # 'year': year,
                    }
                }

                lives.append({
                    'label': title,
                    'fanart': image,
                    'thumb': image,
                    'url': common.PLUGIN.get_url(
                        action='channel_entry',
                        next='play_l',
                        id_diffusion=id_diffusion
                    ),
                    'is_playable': True,
                    'info': info,
                    'context_menu': context_menu
                })

        for live in list_lives_parserjson["page"]["upcoming-lives"]:

            title = live["title"]
            image = live["image"]["large_16_9"]
            # id_diffusion = live["sivideo-id"]

            try:
                value_date = time.strftime(
                    '%d/%m/%Y %H:%M', time.localtime(live["start"]))
            except Exception:
                value_date = ''
            plot = 'Live start at ' + value_date

            info = {
                'video': {
                    'title': title,
                    'plot': plot,
                    # 'aired': aired,
                    # 'date': date,
                    'duration': duration,
                    # 'year': year,
                }
            }

            lives.append({
                'label': title,
                'fanart': image,
                'thumb': image,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='list_live'
                ),
                'is_playable': False,
                'info': info,
                'context_menu': context_menu
            })

    elif params.channel_name == 'franceinfo':

        title = '%s Live' % params.channel_name

        info = {
            'video': {
                'title': title,
                'plot': plot,
                'date': date,
                'duration': duration
            }
        }

        lives.append({
            'label': title,
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='play_l'
            ),
            'is_playable': True,
            'info': info,
            'context_menu': context_menu
        })

    elif params.channel_name == 'la_1ere':

        for id_stream, title_stream in LIVE_LA_1ERE.iteritems():
            title = '%s Live' % title_stream

            info = {
                'video': {
                    'title': title,
                    'plot': plot,
                    'date': date,
                    'duration': duration
                }
            }

            lives.append({
                'label': title,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='play_l',
                    id_stream=id_stream
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

    elif params.channel_name == 'france3regions':

        for id_stream, title_stream in LIVE_FR3_REGIONS.iteritems():
            title = '%s Live' % title_stream

            info = {
                'video': {
                    'title': title,
                    'plot': plot,
                    'date': date,
                    'duration': duration
                }
            }

            lives.append({
                'label': title,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='play_l',
                    id_stream=id_stream
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

    else:
        url_json_live = CHANNEL_LIVE % (params.channel_name)
        file_path_live = utils.download_catalog(
            url_json_live,
            'live_%s.json' % (
                params.channel_name))
        file_prgm_live = open(file_path_live).read()
        json_parser_live = json.loads(file_prgm_live)
        emissions_live = json_parser_live['reponse']['emissions']

        for emission in emissions_live:
            start_time_emission = 'Début : ' + \
                emission['date_diffusion'].split('T')[1].encode('utf-8')

            if emission['accroche']:
                plot = start_time_emission + '\n ' + \
                    emission['accroche'].encode('utf-8')
            elif emission['accroche_programme']:
                plot = start_time_emission + '\n ' + \
                    emission['accroche_programme'].encode('utf-8')
            if emission['date_diffusion']:
                date = emission['date_diffusion']
                date = date.encode('utf-8')
            if emission['duree']:
                duration = int(emission['duree']) * 60
            if emission['titre']:
                title = emission['titre'].encode('utf-8')

            if emission['genre'] != '':
                genre = \
                    emission['genre'].encode('utf-8')

            episode = 0
            if 'episode' in emission:
                episode = emission['episode']

            season = 0
            if 'saison' in emission:
                season = emission['saison']

            cast = []
            director = ''
            if emission['realisateurs'] in emission:
                director = emission['realisateurs'].encode('utf-8')
            if emission['acteurs'] in emission:
                cast.append(emission['acteurs'].encode('utf-8'))

            year = int(date[:4])
            month = int(date[5:7])
            day = int(date[8:10])
            aired = '-'.join((str(year), str(month), str(day)))

            image = URL_IMG % (emission['image_large'])

            info = {
                'video': {
                    'title': title,
                    'plot': plot,
                    'aired': aired,
                    'date': date,
                    'duration': duration,
                    # year': year,
                    'genre': genre,
                    'mediatype': 'tvshow',
                    'season': season,
                    'episode': episode,
                    'cast': cast,
                    'director': director
                }
            }

            lives.append({
                'label': title,
                'fanart': image,
                'thumb': image,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='play_l',
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

    return common.PLUGIN.create_listing(
        lives,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title()
    )


# @common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_video_url(params):
    """Get video URL and start video player"""

    if params.next == 'play_r' or params.next == 'download_video':
        file_prgm = utils.get_webcontent(SHOW_INFO % (params.id_diffusion))
        json_parser = json.loads(file_prgm)

        desired_quality = common.PLUGIN.get_setting('quality')

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
                    all_datas_videos_path.append(video['url'])

            seleted_item = common.sp.xbmcgui.Dialog().select(
                _('Choose video quality'),
                all_datas_videos_quality)

            if seleted_item == -1:
                return None

            url_selected = all_datas_videos_path[seleted_item]

        elif desired_quality == "BEST":
            for video in json_parser['videos']:
                if video['format'] == 'hls_v5_os':
                    url_selected = video['url']
        else:
            for video in json_parser['videos']:
                if video['format'] == 'm3u8-download':
                    url_selected = video['url']

        return url_selected

    elif params.next == 'play_l':

        if params.channel_name == 'la_1ere' or \
                params.channel_name == 'france3regions':
            file_prgm = utils.get_webcontent(
                LIVE_INFO % (params.id_stream))
        elif params.channel_name == 'francetvsport':
            file_prgm = utils.get_webcontent(
                SHOW_INFO % (params.id_diffusion))
        else:
            file_prgm = utils.get_webcontent(
                LIVE_INFO % (params.channel_name))

        json_parser = json.loads(file_prgm)

        url_protected = ''
        for video in json_parser['videos']:
            if 'hls_v1_os' in video['format'] and \
                    video['geoblocage'] is not None:
                url_protected = video['url']

        file_prgm2 = utils.get_webcontent(HDFAUTH_URL % (url_protected))
        json_parser2 = json.loads(file_prgm2)

        return json_parser2['url']


def search(params):
    """Show keyboard to search a program"""
    keyboard = common.sp.xbmc.Keyboard(
        default='',
        title='',
        hidden=False)
    keyboard.doModal()
    if keyboard.isConfirmed():
        query = keyboard.getText()
        params['next'] = 'list_videos_search'
        params['page'] = '0'
        params['query'] = query
        return list_videos(params)

    else:
        return None
