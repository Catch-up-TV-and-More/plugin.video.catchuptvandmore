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

import re
from resources.lib import utils
from resources.lib import common

# TO DO
# Dailymotion JARVIS

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

URL_DAILYMOTION_EMBED = 'http://www.dailymotion.com/embed/video/%s'
# Video_id

def get_stream_dailymotion(video_id):

    desired_quality = common.PLUGIN.get_setting('quality')

    # This Code not working in Jarvis ? TO DO

    url_dmotion = URL_DAILYMOTION_EMBED % (video_id)
    html_video = utils.get_webcontent(url_dmotion)
    html_video = html_video.replace('\\', '')
    url_video_auto = re.compile(
        r'{"type":"application/x-mpegURL","url":"(.*?)"'
        ).findall(html_video)[0]
    m3u8_video_auto = utils.get_webcontent(url_video_auto)
    # Case no absolute path in the m3u8
    # (TO DO how to build the absolute path ?) add quality after
    if 'http' not in  m3u8_video_auto:
        return url_video_auto
    # Case absolute path in the m3u8
    else:
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
