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

import ast
import re
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common

# TO DO
# Get Image KO there is this caracter '|' in the url (not working in Kodi)
# Dailymotion Not working on Jarvis
# Create resolver.py and move Dailymotion code in it

URL_ROOT = 'https://video.autoplus.fr'

URL_DAILYMOTION_EMBED = 'http://www.dailymotion.com/embed/video/%s'
# Video_id

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

context_menu = []
context_menu.append(utils.vpn_context_menu_item())


def channel_entry(params):
    """Entry function of the module"""
    if 'root' in params.next:
        return root(params)
    if 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'play' in params.next:
        return get_video_url(params)
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def root(params):
    """Add modes in the listing"""
    modes = []

    category_title = _('All videos')

    modes.append({
        'label': category_title,
        'url': common.PLUGIN.get_url(
            action='channel_entry',
            next='list_videos_1',
            title=category_title,
            page='1',
            window_title=category_title
        ),
        'context_menu': context_menu
    })

    return common.PLUGIN.create_listing(
        modes,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_LABEL,
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []
    if 'previous_listing' in params:
        videos = ast.literal_eval(params['previous_listing'])

    if params.next == 'list_videos_1':

        replay_episodes_html = utils.get_webcontent(
            URL_ROOT + '/?page=%s' % params.page)
        replay_episodes_soup = bs(replay_episodes_html, 'html.parser')
        episodes = replay_episodes_soup.find_all(
            'div', class_='col-xs-6 col-sm-12')

        for episode in episodes:
            video_title = episode.find('img').get('alt')
            video_url = episode.find('a').get('href')
            video_img = episode.find(
                'img').get('src').encode('utf-8')
            video_duration = 0

            info = {
                'video': {
                    'title': video_title,
                    # 'aired': aired,
                    # 'date': date,
                    'duration': video_duration,
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
                    next='play_r',
                    video_url=video_url
                ),
                'is_playable': True,
                'info': info,
                'context_menu': context_menu
            })

        # More videos...
        videos.append({
            'label': '# ' + common.ADDON.get_localized_string(30100),
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='list_videos_1',
                page=str(int(params.page) + 1),
                update_listing=True,
                previous_listing=str(videos)
            ),
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
def get_video_url(params):
    """Get video URL and start video player"""
    desired_quality = common.PLUGIN.get_setting('quality')

    video_html = utils.get_webcontent(params.video_url)
    # Get DailyMotion Id Video
    video_id = re.compile(
        r'embed/video/(.*?)[\"\?]').findall(
        video_html)[0]
    url_dmotion = URL_DAILYMOTION_EMBED % (video_id)
    html_video = utils.get_webcontent(url_dmotion)
    html_video = html_video.replace('\\', '')
    url_video_auto = re.compile(
        r'{"type":"application/x-mpegURL","url":"(.*?)"'
        ).findall(html_video)[0]
    m3u8_video_auto = utils.get_webcontent(url_video_auto)
    lines = m3u8_video_auto.splitlines()
    if desired_quality == "DIALOG":
        all_datas_videos_quality = []
        all_datas_videos_path = []
        for k in range(0, len(lines) - 1):
            if 'RESOLUTION=' in lines[k]:
                all_datas_videos_quality.append(
                    re.compile(
                    r'RESOLUTION=(.*?),').findall(
                    lines[k])[0])
                all_datas_videos_path.append(
                    lines[k + 1])
        seleted_item = common.sp.xbmcgui.Dialog().select(
            _('Choose video quality'),
            all_datas_videos_quality)
        return all_datas_videos_path[seleted_item].encode(
            'utf-8')
    elif desired_quality == 'BEST':
        # Last video in the Best
        for k in range(0, len(lines) - 1):
            if 'RESOLUTION=' in lines[k]:
                url = lines[k + 1]
        return url
    else:
        for k in range(0, len(lines) - 1):
            if 'RESOLUTION=' in lines[k]:
                url = lines[k + 1]
            break
        return url
