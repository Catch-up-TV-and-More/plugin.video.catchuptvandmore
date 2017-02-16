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

# Recherche par texte
# dernières vidéos de la chaine (triées par date ajout)
    # tout
    # catégorie ..
# Liste A à Z
# Si FR3 ou FR1 : Régions


import json
from resources.lib import utils
from resources.lib import common

channel_catalog = 'http://pluzz.webservices.francetelevisions.fr/' \
                  'pluzz/liste/type/replay/nb/10000/chaine/%s'

show_info = 'http://webservices.francetelevisions.fr/tools/' \
            'getInfosOeuvre/v2/?idDiffusion=%s&catalogue=Pluzz'

url_img = 'http://refonte.webservices.francetelevisions.fr%s'

url_search = 'https://pluzz.webservices.francetelevisions.fr/' \
             'mobile/recherche/nb/20/tri/date/requete/%s/debut/0'

categories = {"france2": "France 2",
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
              "saintpierreetmiquelon": "St-Pierre et Miquelon 1ère",
              "wallisetfutuna": "Wallis et Futuna 1ère",
              "sport": "Sport",
              "info": "Info",
              "documentaire": "Documentaire",
              "seriefiction": "Série & fiction",
              "magazine": "Magazine",
              "jeunesse": "Jeunesse",
              "divertissement": "Divertissement",
              "jeu": "Jeu",
              "culture": "Culture"}


def channel_entry(params):
    if 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_URL(params)
    elif 'search' in params.next:
        return search(params)


@common.plugin.cached(common.cache_time)
def list_shows(params):
    shows = []
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

    url_json = channel_catalog % (real_channel)
    file_path = utils.download_catalog(
        url_json,
        '%s.json' % (params.channel_name))
    file_prgm = open(file_path).read()
    json_parser = json.loads(file_prgm)
    emissions = json_parser['reponse']['emissions']

    if params.next == 'list_shows_1':
        for emission in emissions:
            rubrique = emission['rubrique'].encode('utf-8')
            if rubrique not in unique_item:
                unique_item[rubrique] = rubrique
                rubrique_title = change_to_nicer_name(rubrique)

                shows.append({
                    'label': rubrique_title,
                    'url': common.plugin.get_url(
                        action='channel_entry',
                        rubrique=rubrique,
                        next='list_shows_2'
                    )
                })

        shows.append({
            'label': common.addon.get_localized_string(30103),
            'url': common.plugin.get_url(
                action='channel_entry',
                next='search'
            )
        })

        sort_methods = (
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        )

        shows = common.plugin.create_listing(
            shows,
            sort_methods=sort_methods
        )

    elif params.next == 'list_shows_2':
        for emission in emissions:
            rubrique = emission['rubrique'].encode('utf-8')
            if rubrique == params.rubrique:
                titre_programme = emission['titre_programme'].encode('utf-8')
                if titre_programme != '':
                    id_programme = emission['id_programme'].encode('utf-8')
                    if id_programme == '':
                        id_programme = emission['id_emission'].encode('utf-8')
                    if id_programme not in unique_item:
                        unique_item[id_programme] = id_programme
                        icon = url_img % (emission['image_large'])
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
                            'url': common.plugin.get_url(
                                action='channel_entry',
                                next='list_videos_1',
                                id_programme=id_programme,
                                search=False
                            ),
                            'info': info
                        })

        sort_methods = (
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        )

        shows = common.plugin.create_listing(
            shows,
            content='tvshows',
            sort_methods=sort_methods
        )

    return shows


@common.plugin.cached(common.cache_time)
def change_to_nicer_name(original_name):
    if original_name in categories:
        return categories[original_name]
    return original_name


@common.plugin.cached(common.cache_time)
def list_videos(params):
    videos = []
    if params.search:
        file_path = params.file_search
    else:
        file_path = utils.download_catalog(
            channel_catalog % (params.channel_name),
            '%s.json' % (params.channel_name)
        )
    file_prgm = open(file_path).read()
    json_parser = json.loads(file_prgm)
    emissions = json_parser['reponse']['emissions']
    for emission in emissions:
        id_programme = emission['id_programme'].encode('utf-8')
        if id_programme == '':
            id_programme = emission['id_emission'].encode('utf-8')
        if params.search or id_programme == params.id_programme:
            title = ''
            plot = ''
            duration = 0
            date = ''
            genre = ''
            id_diffusion = emission['id_diffusion']
            file_prgm = utils.get_webcontent(
                show_info % (emission['id_diffusion']))
            if(file_prgm != ''):
                json_parserShow = json.loads(file_prgm)
                if json_parserShow['synopsis']:
                    plot = json_parserShow['synopsis'].encode('utf-8')
                if json_parserShow['diffusion']['date_debut']:
                    date = json_parserShow['diffusion']['date_debut']
                    date = date.encode('utf-8')
                if json_parserShow['real_duration']:
                    duration = int(json_parserShow['real_duration'])
                if json_parserShow['titre']:
                    title = json_parserShow['titre'].encode('utf-8')
                if json_parserShow['sous_titre']:
                    title = ' '.join((
                        title,
                        '- [I]',
                        json_parserShow['sous_titre'].encode('utf-8'),
                        '[/I]'))

                if json_parserShow['genre'] != '':
                    genre = \
                        json_parserShow['genre'].encode('utf-8')

                year = int(date[6:10])
                day = date[:2]
                month = date[3:5]
                date = '.'.join((day, month, str(year)))
                aired = '-'.join((str(year), month, day))
                # date : string (%d.%m.%Y / 01.01.2009)
                # aired : string (2008-12-07)
                image = url_img % (json_parserShow['image'])
                info = {
                    'video': {
                        'title': title,
                        'plot': plot,
                        'aired': aired,
                        'date': date,
                        'duration': duration,
                        'year': year,
                        'genre': genre
                    }
                }

                videos.append({
                    'label': title,
                    'thumb': image,
                    'url': common.plugin.get_url(
                        action='channel_entry',
                        next='play',
                        id_diffusion=id_diffusion
                    ),
                    'is_playable': True,
                    'info': info
                })

    sort_methods = (
        common.sp.xbmcplugin.SORT_METHOD_DATE,
        common.sp.xbmcplugin.SORT_METHOD_DURATION,
        common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
        common.sp.xbmcplugin.SORT_METHOD_UNSORTED
    )
    return common.plugin.create_listing(
        videos,
        sort_methods=sort_methods,
        content='tvshows')


@common.plugin.cached(common.cache_time)
def get_video_URL(params):
        file_prgm = utils.get_webcontent(show_info % (params.id_diffusion))
        json_parser = json.loads(file_prgm)
        url_HD = ''
        url_SD = ''
        for video in json_parser['videos']:
            if video['format'] == 'hls_v5_os':
                url_HD = video['url']
            if video['format'] == 'm3u8-download':
                url_SD = video['url']

        disered_quality = common.plugin.get_setting(
            params.channel_id + '.quality')

        if disered_quality == 'HD' and url_HD is not None:
            return url_HD
        else:
            return url_SD


def search(params):
    keyboard = common.sp.xbmc.Keyboard(
        default='',
        title='',
        hidden=False)
    keyboard.doModal()
    if keyboard.isConfirmed():
        query = keyboard.getText()
        json_path = utils.download_catalog(
            url_search % query,
            '%s_search.json' % params.channel_name,
            force_dl=True)

        params['search'] = True
        params['file_search'] = json_path
        return list_videos(params)

    else:
        return None
