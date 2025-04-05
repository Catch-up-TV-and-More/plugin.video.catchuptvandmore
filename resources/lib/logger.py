
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, SylvainCecchetto, wwark
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from kodi_six import xbmc, xbmcaddon
from .constants import LOGGER_ID

class Logger(object):
    default_level = xbmc.LOGDEBUG

    def log(self, text, log_level=default_level):
        log_line = '[%s] %s' % (LOGGER_ID, text)
        xbmc.log(msg=log_line, level=log_level)

    def debug(self, text):
        self.log(text, xbmc.LOGDEBUG)

    def info(self, text):
        self.log(text, xbmc.LOGINFO)

    def notice(self, text):
        self.log(text, xbmc.LOGNOTICE)

    def warning(self, text):
        self.log(text, xbmc.LOGWARNING)

    def error(self, text):
        self.log(text, xbmc.LOGERROR)
