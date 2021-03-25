# -*- coding: utf-8 -*-
# Copyright: (c) 2017, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import re
import json
import requests

from codequick import Resolver
from kodi_six import xbmcgui
from resources.lib import web_utils
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

# TO DO
# Add Paid contents ?

URL_ROOT = 'https://live-replay.%s.be'

URL_ROOT_LOGIN = 'https://app.auth.digital.abweb.com'

URL_CONNECT_AUTHORIZE = URL_ROOT_LOGIN + '/connect/authorize'

URL_ACCOUNT_LOGIN = URL_ROOT_LOGIN + '/Account/Login'

URL_CONNECT_TOKEN = URL_ROOT_LOGIN + '/connect/token'

URL_AUTH_CALLBACK = URL_ROOT + '/auth-callback'

URL_API = 'https://subscription.digital.api.abweb.com/api/subscription/has-live-rights/%s/%s'


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    # Using script (https://github.com/Catch-up-TV-and-More/plugin.video.catchuptvandmore/issues/484)

    # Create session
    # KO - session_urlquick = urlquick.Session()
    session_requests = requests.session()

    # TODO find those values
    state = 'b71f9b79703240fe967552544f5ea1b9'
    code_challenge = '89bnNcjz_0ynNMV8cjtMWPWcPIyEU1oFwQqD9YfKRkA'
    params = {
        'client_id': item_id,
        'redirect_uri': URL_AUTH_CALLBACK % item_id,
        'response_type': 'code',
        'scope': 'openid profile email',
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
        'response_mode': 'query',
        'action': 'undefined'
    }
    paramsencoded = urlencode(params)

    # Get Token
    # KO - resp = session_urlquick.get(URL_COMPTE_LOGIN)
    resp = session_requests.get(URL_CONNECT_AUTHORIZE, params=params)
    value_token = re.compile(
        r'__RequestVerificationToken\" type\=\"hidden\" value\=\"(.*?)\"').findall(resp.text)[0]
    if plugin.setting.get_string('abweb.login') == '' or \
            plugin.setting.get_string('abweb.password') == '':
        xbmcgui.Dialog().ok(
            'Info',
            plugin.localize(30604) %
            ('ABWeb', 'http://www.abweb.com/BIS-TV-Online/abonnement.aspx'))
        return False
    # Build PAYLOAD
    payload = {
        "__RequestVerificationToken":
        value_token,
        "Email":
        plugin.setting.get_string('abweb.login'),
        "Password":
        plugin.setting.get_string('abweb.password'),
        "button":
        'login'
    }
    paramslogin = {
        'ReturnUrl': '/connect/authorize/callback?%s' % paramsencoded
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    post_url = URL_ACCOUNT_LOGIN + '?%s' % urlencode(paramslogin)
    # LOGIN
    # KO - resp2 = session_urlquick.post(
    #     URL_COMPTE_LOGIN, data=payload,
    #     headers={'User-Agent': web_utils.get_ua, 'referer': URL_COMPTE_LOGIN})
    resp2 = session_requests.post(post_url,
                                  data=payload,
                                  headers=headers,
                                  verify=False)
    next_url = resp2.history[1].headers['location']
    code_value = re.compile(r'code\=(.*?)\&').findall(next_url)[0]

    code_verifier = '8111a6c1025249fd9c0ff43f5af8d37b8929eb1a06f342659c7e3ff6becb763bfcc752ec316f44f385523f02ef90ac77'
    paramtoken = {
        'client_id': item_id,
        'code': code_value,
        'redirect_uri': URL_AUTH_CALLBACK % item_id,
        'code_verifier': code_verifier,
        'grant_type': 'authorization_code'
    }
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Length': '296',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'app.auth.digital.abweb.com',
        'Origin': 'https://www.bistvonline.com',
        'Referer': 'https://www.bistvonline.com/',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': web_utils.get_random_ua()
    }
    resp3 = session_requests.post(URL_CONNECT_TOKEN, headers=headers, data=paramtoken)
    json_parser3 = json.loads(resp3.text)
    token = json_parser3['id_token']

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': 'Bearer %s' % token,
        'User-Agent': web_utils.get_random_ua(),
        'Referer': 'https://www.bistvonline.com/live'
    }
    resp4 = session_requests.get(URL_API % (item_id, item_id), headers=headers)
    json_parser4 = json.loads(resp4.text)
    return json_parser4['hlsUrl']
