# -*- coding: utf-8 -*-
# Copyright: (c) JUL1EN094, SPM, SylvainCecchetto
# Copyright: (c) 2016, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import json
from builtins import str

import inputstreamhelper
import urlquick
from codequick import Listitem, Resolver, Route, Script, utils
from kodi_six import xbmcgui, xbmcplugin
from resources.lib import web_utils
from resources.lib.addon_utils import get_item_media_path
from resources.lib.kodi_utils import (INPUTSTREAM_PROP, get_selected_item_art,
                                      get_selected_item_info,
                                      get_selected_item_label)
from resources.lib.menu_utils import item_post_treatment

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    URL_CERTIFICATE = "https://lic.drmtoday.com/license-server-fairplay/cert/m6_salto"
    URL_LICENSE = "https://lic.drmtoday.com/license-server-fairplay"
    URL_STREAM = "https://origin-live-salto.video.bedrock.tech/salto/long/enc/ftv2/noscte/hdbindex.m3u8"

    MAIL = "cecchetto.sylvain@me.com"
    PWD = "cobhy2-fydmup-cafVyj"

    URL_LOGIN = "https://login.salto.fr/accounts.login"

    URL_TIME = "https://time.salto.fr"
    URL_JWT = "https://front-auth.salto.fr/v2/platforms/m6group_web/getJwt"
    URL_MENU = "https://layout.salto.fr/front/v1/salto/m6group_web/main/token-web-3/navigation/desktop"


    s = urlquick.Session()

    # Login
    data = {
        "loginID": "cecchetto.sylvain@me.com",
        "password": "cobhy2-fydmup-cafVyj",
        "sessionExpiration": -2,
        "targetEnv": "jssdk",
        "include": "profile,data",
        "includeUserInfo": True,
        "lang": "fr",
        "APIKey": "3_nHh1rdsQ9v8WTUvRNFtOJS1v5nPAl6nqTxbzMsVCckVqD5QN7HsXRu_FKqUp5kjw",
        "sdk": "js_latest",
        "authMode": "cookie",
        "pageURL": "https://www.salto.fr/",
        "sdkBuild": 12563,
        "format": "json",
    }
    login_infos = s.post(URL_LOGIN, data=data).json()


    # Get JWT
    headers = {
        # 'X-Auth-Token': '7cb06bd6abbb950095d86f48102f68c491c24414',
        # 'X-Auth-Token-Timestamp': str(timestamp),
        'x-auth-device-id': '134cb737accab7062c3dcb1ef15667e3ba2ea29362bb83b1259c600317e13905',
        # 'X-Client-Release': '5.26.0',
        'X-Auth-gigya-uid': login_infos['UID'],
        'X-Auth-gigya-signature': login_infos['UIDSignature'],
        'X-Auth-gigya-signature-timestamp': login_infos['signatureTimestamp'],
        # 'Host': 'front-auth.salto.fr',
        # 'Accept': '*/*',
        # 'X-Customer-Name': 'salto',
        # 'Accept-Encoding': 'gzip;q=1.0, compress;q=0.5',
        # 'Accept-Language': 'fr-FR;q=1.0, en-GB;q=0.9',
        # 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0',
    }
    token = s.get(URL_JWT, headers=headers, max_age=-1).json()['token']
    print('TOKEN', token)

    item = Listitem()
    item.path = URL_STREAM
    item.label = "FR2"
    item.property['fairplay.license_url'] = URL_LICENSE
    item.property['fairplay.license_headers'] = 'x-dt-auth-token=' + token + "&Content-Type=application/octet-stream"
    item.property['fairplay.certificate_url'] = URL_CERTIFICATE
    return item
