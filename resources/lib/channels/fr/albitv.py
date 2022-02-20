# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Joaopa
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

import re

from codequick import Resolver
import urlquick

from resources.lib import web_utils


# TODO
# Add Replay

URL_ROOT = "https://www.albi-tv.fr"

URL_LIVE = "https://www.creacast.com/play.php?su=albi-tv-ch1"


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    resp = urlquick.get(URL_LIVE, headers={"User-Agent": web_utils.get_random_ua()}, max_age=-1)
    return re.compile(r'file: "(.*?)[\?\"]').findall(resp.text)[0]
