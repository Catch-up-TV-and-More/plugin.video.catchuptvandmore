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

import json
import re
from bs4 import BeautifulSoup as bs
from resources.lib import utils
from resources.lib import common

# TO DO
# Live TV
# KO Download Mode | How to fix ?
# Get policyID, Player (build url platform)
# Implement this case 'if len(replay_show_seasons) == 0'

URL_ROOT = 'http://www.nbc.com'

URL_SHOWS = 'https://www.nbc.com/shows/all'

URL_SHOW_SEASON = 'https://www.nbc.com/%s/episodes/season-%s'
# show_name, season_number

URL_VIDEOS = 'https://api.nbc.com/v3.14/videos?filter[entitlement]' \
             '=free&filter[published]=1&include=image&sort=airdate' \
             '&filter[show]=%s&filter[seasonNumber]=%s'
# Get 50 videos (more add a button)
# ShowId, SeasonID

URL_STREAM = 'http://link.theplatform.com/s/NnzsPC/media/%s?policy=%s' \
             '&player=%s&formats=m3u,mpeg4&format=SMIL&embedded=true&' \
             'tracking=true'
# IdChannel (NnzsPC), VideoId, policyId, player

URL_VIDEO_INFO = 'http://link.theplatform.com/s/NnzsPC/media/guid/%s' \
                 '?format=preview'
# IdChannel (NnzsPC), Guid

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

def channel_entry(params):
    """Entry function of the module"""
    if 'root' in params.next:
        return root(params)
    if 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'live' in params.next:
        return list_live(params)
    elif 'play' in params.next:
        return get_video_url(params)
    return None

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def root(params):
    """Add modes in the listing"""
    modes = []

    # Add Replay
    modes.append({
        'label' : 'Replay',
        'url': common.PLUGIN.get_url(
            action='channel_entry',
            next='list_shows_1',
            category='%s Replay' % params.channel_name.upper(),
            window_title='%s Replay' % params.channel_name.upper()
        ),
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

        file_path = utils.download_catalog(
            URL_SHOWS,
            '%s_shows.html' % (params.channel_name)
        )
        replay_shows_html = open(file_path).read()
        replay_shows_json_in_html = re.compile(
            '<script>PRELOAD=(.*?)</script>').findall(replay_shows_html)[0]
        replay_shows_json = json.loads(replay_shows_json_in_html)

        replay_shows = replay_shows_json['allShows']

        for show in replay_shows:

            show_title = show['title'].encode('utf-8')
            show_img = show['image']['path'].encode('utf-8')
            show_url = URL_ROOT + '/' + show['urlAlias'] + '?nbc=1'

            shows.append({
                'label': show_title,
                'thumb': show_img,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='list_shows_2',
                    title=show_title,
                    show_url=show_url,
                    show_alias=show['urlAlias'],
                    window_title=show_title
                    )
                })

    elif params.next == 'list_shows_2':

        file_path = utils.download_catalog(
            params.show_url,
            '%s_show_%s.html' % (params.channel_name, params.title)
        )
        replay_show_html = open(file_path).read()

        replay_show_seasons_soup = bs(replay_show_html, 'html.parser')
        replay_show_seasons = replay_show_seasons_soup.find_all(
            'span', class_='filter-select__link')

        for season in replay_show_seasons:

            season_title = season.get_text().encode('utf-8')
            show_season_url = URL_SHOW_SEASON % (
                params.show_alias, season_title.split(' ')[1])

            shows.append({
                'label': season_title,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='list_videos_1',
                    title=season_title,
                    show_season_url=show_season_url,
                    show_alias=params.show_alias,
                    window_title=season_title
                    )
                })

        #TO DO if len(replay_show_seasons) == 0

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []

    file_path = utils.download_catalog(
        params.show_season_url,
        '%s_show_%s_%s.html' % (
            params.channel_name,
            params.show_alias,
            params.title)
    )
    replay_show_season_html = open(file_path).read()
    show_id = re.compile('"entities":{"(.*?)"').findall(
        replay_show_season_html)[0]

    file_path_json = utils.download_catalog(
        URL_VIDEOS % (show_id, params.title.split(' ')[1]),
        '%s_show_%s_%s.json' % (params.channel_name, show_id, params.title)
    )
    replay_episodes_season_json = open(file_path_json).read()
    episodes_season_parser = json.loads(replay_episodes_season_json)

    for episode in episodes_season_parser['data']:

        #Get GUID Episode
        guid_episode = episode['attributes'].get(
            'embedUrl').split('guid/')[1].split('?')[0]

        episode_path_json = utils.download_catalog(
            URL_VIDEO_INFO % guid_episode,
            '%s_show_episode_%s.json' % (
                params.channel_name,
                guid_episode)
        )
        episode_show_json = open(episode_path_json).read()
        episode_show_json_parser = json.loads(episode_show_json)

        video_title = 'S%sE%s - ' % (
            episode_show_json_parser['nbcu$seasonNumber'],
            episode_show_json_parser['nbcu$airOrder']) + episode_show_json_parser['title']
        video_plot = episode_show_json_parser.get('description')
        video_duration = 0
        video_img = episode_show_json_parser.get('defaultThumbnailUrl')
        video_id = episode_show_json_parser['mediaPid']

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

        download_video = (
            _('Download'),
            'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                action='download_video',
                video_id=video_id) + ')'
        )
        context_menu = []
        context_menu.append(download_video)

        videos.append({
            'label': video_title,
            'thumb': video_img,
            'fanart': video_img,
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='play_r',
                video_id=video_id
            ),
            'is_playable': True,
            'info': info,
            'context_menu': context_menu
        })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
            common.sp.xbmcplugin.SORT_METHOD_GENRE,
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        content='tvshows',
        category=common.get_window_title()
    )

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_live(params):
    return None

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_r' or params.next == 'download_video':
        url_to_get_stream = 'http://link.theplatform.com/s/NnzsPC/media/'+params.video_id+'?policy=43674&player=NBC.com%20Instance%20of%3A%20rational-player-production&formats=m3u,mpeg4&format=SMIL&embedded=true&tracking=true'

        file_path = utils.download_catalog(
            url_to_get_stream,
            '%s_episode_%s.html' % (params.channel_name, params.video_id)
        )
        stream_html = open(file_path).read()
        return re.compile('<video src="(.*?)"').findall(stream_html)[0]
    return ''
