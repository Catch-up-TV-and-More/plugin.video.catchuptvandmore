# -*- coding: utf-8 -*-
# Copyright: (c) JUL1EN094, SPM, SylvainCecchetto
# Copyright: (c) 2016, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

import json
import sys
from random import randint

# noinspection PyUnresolvedReferences
from codequick import Script
import urlquick

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

try:  # Python 3
    from urllib.parse import unquote_plus
except ImportError:  # Python 2
    # noinspection PyUnresolvedReferences
    from urllib import unquote_plus

if sys.version_info.major >= 3 and sys.version_info.minor >= 4:
    import html as html_parser
elif sys.version_info.major >= 3:
    import html.parser

    html_parser = html.parser.HTMLParser()
else:
    # noinspection PyUnresolvedReferences
    import HTMLParser

    html_parser = HTMLParser.HTMLParser()


# see https://www.whatismybrowser.com/guides/the-latest-user-agent/windows
windows_user_agents = [
    # Edge on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/125.0.0.0 Safari/537.36 Edg/125.0.2535.51',
    # Chrome on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    # Firefox on windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
    # Vivaldi on Windows
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 '
    'Safari/537.36 Vivaldi/6.7.3329.35'
]

# https://www.whatismybrowser.com/guides/the-latest-user-agent/macos
mac_user_agents = [
    # Safari on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 '
    'Safari/605.1.15',
    # Firefox on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:126.0) Gecko/20100101 Firefox/126.0',
    # Chrome on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 '
    'Safari/537.36',
    # Vivaldi on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 '
    'Safari/537.36 Vivaldi/6.7.3329.35',
    # Edge on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 '
    'Safari/537.36 Edg/125.0.2535.51',
]

linux_user_agents = [
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    '(KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
    'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
]

user_agents = windows_user_agents + mac_user_agents + linux_user_agents


def get_ua():
    """Get first user agent in the 'user_agents' list

    Returns:
        str: User agent
    """
    return user_agents[0]


def get_random_ua():
    """Get a random user agent in the 'user_agents' list

    Returns:
        str: Random user agent
    """
    return user_agents[randint(0, len(user_agents) - 1)]


def get_random_windows_ua():
    return windows_user_agents[randint(0, len(windows_user_agents) - 1)]


# code adapted from weather.weatherbit.io - Thanks Ronie
def geoip():
    """Get country code based on IP address

    Returns:
        str: Country code (e.g. FR)
    """
    # better service - https://geoftv-a.akamaihd.net/ws/edgescape.json
    try:
        resp = urlquick.get('https://geoftv-a.akamaihd.net/ws/edgescape.json', max_age=-1)
        data = json.loads(resp.text)
        if 'reponse' in data:
            return data['reponse']['geo_info']['country_code']
    except Exception:
        pass
    Script.notify(Script.get_info('name'), Script.localize(30724), icon=Script.NOTIFY_WARNING)
    Script.log('Failed to get country code based on IP address', lvl=Script.WARNING)
    return None
