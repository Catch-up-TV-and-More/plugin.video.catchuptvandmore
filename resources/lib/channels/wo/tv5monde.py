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

import json
import re
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common

# TO DO
# Download Mode / QUality Mode
# TV5Monde+, TIVI5+

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

context_menu = []
context_menu.append(utils.vpn_context_menu_item())

URL_TV5MAF_ROOT = 'https://afrique.tv5monde.com'

URL_TV5MONDE_LIVE = 'http://live.tv5monde.com/'


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
    return None


LIST_LIVE_TV5MONDE = {
    _('Live TV') + ' France Belgique Suisse': 'fbs',
    _('Live TV') + ' Info Plus': 'infoplus'
}

LIST_LIVE_TIVI5MONDE = {
    _('Live TV') + ' TIVI 5Monde': 'tivi5monde'
}


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def root(params):
    modes = []

    # Add Replay
    if params.channel_name != 'tv5monde' and \
       params.channel_name != 'tivi5monde':
        modes.append({
            'label': 'Replay',
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='list_shows_1',
                category='%s Replay' % params.channel_name.upper(),
                window_title='%s Replay' % params.channel_name.upper()
            ),
            'context_menu': context_menu
        })

    # Add Live
    if params.channel_name != 'tv5mondeafrique':
        modes.append({
            'label': _('Live TV'),
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='live_cat',
                category='%s Live TV' % params.channel_name.upper(),
                window_title='%s Live TV' % params.channel_name.upper()
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

    if params.next == 'list_shows_1':
        if params.channel_name == 'tv5mondeafrique':
            list_categories_html = utils.get_webcontent(
                URL_TV5MAF_ROOT + '/videos')
            list_categories_soup = bs(
                list_categories_html, 'html.parser')
            list_categories = list_categories_soup.find_all(
                'h2', class_='tv5-title tv5-title--beta u-color--goblin')

            for category in list_categories:

                category_title = category.find(
                    'a').get_text().encode('utf-8')
                category_url = URL_TV5MAF_ROOT + category.find(
                    'a').get('href').encode('utf-8')

                shows.append({
                    'label': category_title,
                    'url': common.PLUGIN.get_url(
                        action='channel_entry',
                        next='list_shows_2',
                        title=category_title,
                        category_url=category_url,
                        window_title=category_title
                    ),
                    'context_menu': context_menu
                })

    elif params.next == 'list_shows_2':
        if params.channel_name == 'tv5mondeafrique':

            list_shows_html = utils.get_webcontent(
                params.category_url)
            list_shows_soup = bs(list_shows_html, 'html.parser')
            list_shows = list_shows_soup.find_all(
                'div', class_='grid-col-12 grid-col-m-4')

            for show in list_shows:

                show_title = show.find('h2').get_text(
                    ).strip().encode('utf-8')
                show_url = URL_TV5MAF_ROOT + show.find(
                    'a').get('href').encode('utf-8')
                if 'http' in show.find('img').get('src'):
                    show_image = show.find('img').get(
                        'src').encode('utf-8')
                else:
                    show_image = URL_TV5MAF_ROOT + show.find('img').get(
                        'src').encode('utf-8')

                shows.append({
                    'label': show_title,
                    'thumb': show_image,
                    'url': common.PLUGIN.get_url(
                        action='channel_entry',
                        next='list_videos_1',
                        title=show_title,
                        category_url=show_url,
                        window_title=show_title
                    ),
                    'context_menu': context_menu
                })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []

    if params.next == 'list_videos_1':
        if params.channel_name == 'tv5mondeafrique':

            replay_videos_html = utils.get_webcontent(
                params.category_url)
            replay_videos_soup = bs(replay_videos_html, 'html.parser')
            if replay_videos_soup.find('div',
                class_='u-bg--concrete u-pad-t--xl u-pad-b--l') is None:

                data_video = replay_videos_soup.find(
                    'div', class_='tv5-player')

                video_title = data_video.find('h1').get_text(
                    ).strip().encode('utf-8')
                video_img = re.compile(
                    r'image\" content=\"(.*?)\"').findall(
                    replay_videos_html)[0]
                video_plot = data_video.find('div',
                    class_='tv5-desc to-expand u-mg-t--m u-mg-b--s').get_text(
                    ).strip().encode('utf-8')

                info = {
                    'video': {
                        'title': video_title,
                        # 'aired': aired,
                        # 'date': date,
                        # 'duration': video_duration,
                        'plot': video_plot,
                        # 'year': year,
                        'mediatype': 'tvshow'
                    }
                }

                download_video = (
                    _('Download'),
                    'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                        action='download_video',
                        video_url=params.category_url) + ')'
                )
                context_menu = []
                # context_menu.append(download_video)
                context_menu.append(utils.vpn_context_menu_item())

                videos.append({
                    'label': video_title,
                    'thumb': video_img,
                    'fanart': video_img,
                    'url': common.PLUGIN.get_url(
                        action='channel_entry',
                        next='play_r_tv5mondeafrique',
                        video_url=params.category_url
                    ),
                    'is_playable': True,
                    'info': info,
                    'context_menu': context_menu
                })
            else:
                seasons = replay_videos_soup.find(
                    'div',
                    class_='tv5-pagerTop tv5-pagerTop--green'
                ).find_all('a')
                if len(seasons) > 1:

                    for season in seasons:

                        video_title = 'Saison ' + season.get_text()
                        video_url = URL_TV5MAF_ROOT + season.get(
                            'href').encode('utf-8')

                        info = {
                            'video': {
                                'title': video_title
                            }
                        }

                        videos.append({
                            'label': video_title,
                            'url': common.PLUGIN.get_url(
                                action='channel_entry',
                                next='list_videos_2',
                                category_url=video_url
                            ),
                            'is_playable': False,
                            'info': info,
                            'context_menu': context_menu
                        })
                else:
                    all_videos = replay_videos_soup.find(
                        'div',
                        class_='u-bg--concrete u-pad-t--xl u-pad-b--l'
                    ).find_all(
                        'div',
                        'grid-col-12 grid-col-m-4')

                    for video in all_videos:

                        video_title = video.find('h2').get_text(
                            ).strip().encode('utf-8')
                        video_img = video.find('img').get('src')
                        video_url = URL_TV5MAF_ROOT + video.find(
                            'a').get('href').encode('utf-8')

                        info = {
                            'video': {
                                'title': video_title,
                                # 'aired': aired,
                                # 'date': date,
                                # 'duration': video_duration,
                                # 'plot': video_plot,
                                # 'year': year,
                                'mediatype': 'tvshow'
                            }
                        }

                        download_video = (
                            _('Download'),
                            'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                                action='download_video',
                                video_url=video_url) + ')'
                        )
                        context_menu = []
                        # context_menu.append(download_video)
                        context_menu.append(utils.vpn_context_menu_item())

                        videos.append({
                            'label': video_title,
                            'thumb': video_img,
                            'url': common.PLUGIN.get_url(
                                action='channel_entry',
                                next='play_r_tv5mondeafrique',
                                video_url=video_url
                            ),
                            'is_playable': True,
                            'info': info,
                            'context_menu': context_menu
                        })

    elif params.next == 'list_videos_2':
        if params.channel_name == 'tv5mondeafrique':
            replay_videos_html = utils.get_webcontent(
                params.category_url)
            replay_videos_soup = bs(replay_videos_html, 'html.parser')

            all_videos = replay_videos_soup.find('div',
                class_='u-bg--concrete u-pad-t--xl u-pad-b--l').find_all(
                'div', 'grid-col-12 grid-col-m-4')

            for video in all_videos:

                video_title = video.find('h2').get_text(
                    ).strip().encode('utf-8')
                video_img = video.find('img').get('src')
                video_url = URL_TV5MAF_ROOT + video.find(
                    'a').get('href').encode('utf-8')

                info = {
                    'video': {
                        'title': video_title,
                        # 'aired': aired,
                        # 'date': date,
                        # 'duration': video_duration,
                        # 'plot': video_plot,
                        # 'year': year,
                        'mediatype': 'tvshow'
                    }
                }

                download_video = (
                    _('Download'),
                    'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                        action='download_video',
                        video_url=video_url) + ')'
                )
                context_menu = []
                # context_menu.append(download_video)
                context_menu.append(utils.vpn_context_menu_item())

                videos.append({
                    'label': video_title,
                    'thumb': video_img,
                    'url': common.PLUGIN.get_url(
                        action='channel_entry',
                        next='play_r_tv5mondeafrique',
                        video_url=video_url
                    ),
                    'is_playable': True,
                    'info': info,
                    'context_menu': context_menu
                })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        content='tvshows',
        update_listing='update_listing' in params,
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_live(params):
    """Build live listing"""
    lives = []

    if params.channel_name == 'tv5monde':
        for live_name, live_id in LIST_LIVE_TV5MONDE.iteritems():

            live_title = live_name
            live_html = utils.get_webcontent(
                URL_TV5MONDE_LIVE + '%s.html' % live_id)
            live_json = re.compile(
                r'data-broadcast=\'(.*?)\'').findall(live_html)[0]
            live_json_parser = json.loads(live_json)
            live_url = live_json_parser["files"][0]["url"]
            live_img = URL_TV5MONDE_LIVE + re.compile(
                r'data-image=\"(.*?)\"').findall(live_html)[0]

            info = {
                'video': {
                    'title': live_title
                }
            }

            lives.append({
                'label': live_title,
                'thumb': live_img,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='play_l',
                    live_url=live_url,
                ),
                'is_playable': True,
                'info': info
            })

    elif params.channel_name == 'tivi5monde':

        for live_name, live_id in LIST_LIVE_TIVI5MONDE.iteritems():

            live_title = live_name
            live_html = utils.get_webcontent(
                URL_TV5MONDE_LIVE  + '%s.html' % live_id)
            live_json = re.compile(
                r'data-broadcast=\'(.*?)\'').findall(live_html)[0]
            live_json_parser = json.loads(live_json)
            live_url = live_json_parser["files"][0]["url"]
            live_img = URL_TV5MONDE_LIVE + re.compile(
                r'data-image=\"(.*?)\"').findall(live_html)[0]

            info = {
                'video': {
                    'title': live_title
                }
            }

            lives.append({
                'label': live_title,
                'thumb': live_img,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='play_l',
                    live_url=live_url,
                ),
                'is_playable': True,
                'info': info
            })

    return common.PLUGIN.create_listing(
        lives,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_video_url(params):

    if params.next == 'play_r_tv5mondeafrique':
        info_video_html = utils.get_webcontent(params.video_url)
        video_json = re.compile(
            'data-broadcast=\'(.*?)\'').findall(
            info_video_html)[0]
        video_json = json.loads(video_json)
        return video_json["files"][0]["url"]
    elif params.next == 'play_l':
        return params.live_url
