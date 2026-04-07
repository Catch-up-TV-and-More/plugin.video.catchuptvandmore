# -*- coding: utf-8 -*-
# Copyright: (c) 2025, QValette
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import base64

# noinspection PyUnresolvedReferences
from codequick import Resolver

import urlquick

from resources.lib import resolver_proxy

# Fallback URL used when the dynamic fetch fails
_URL_LIVE_FALLBACK = (
    'https://cmero-ott-live.ssl.cdn.cra.cz/channels/cme-ro-voyo-news/'
    'playlist.m3u8?offsetSeconds=0&url=0'
)

# Stream URL is fetched from the romaniatv.app channels feed
# Source: https://www.romaniatv.app (channelsEndpoint config in its JS bundle)
# The feed stores AES-128-GCM encrypted URLs (key extracted from the site's JS bundle)
_CHANNELS_URL = 'https://gist.githubusercontent.com/nickstamp93/eecc35645ec891c0260ceb038fd07514/raw/ch_ro.json'
_CHANNEL_ID = 905
# Key: String.fromCharCode(100,83,74,99,69,99,114,51,97,115,110,103,74,109,99,52)
_KEY = bytes([100, 83, 74, 99, 69, 99, 114, 51, 97, 115, 110, 103, 74, 109, 99, 52])


def _decrypt_gcm(encrypted_b64):
    try:
        from Crypto.Cipher import AES
    except ImportError:
        from Cryptodome.Cipher import AES
    # Pad base64 string if needed, then decode
    raw = base64.b64decode(encrypted_b64 + '==')
    # Layout: 12-byte nonce | ciphertext | 16-byte auth tag
    nonce = raw[:12]
    tag = raw[-16:]
    ciphertext = raw[12:-16]
    plaintext = AES.new(_KEY, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(ciphertext, tag)
    return plaintext.decode('utf-8')


def _get_live_url():
    try:
        resp = urlquick.get(_CHANNELS_URL, max_age=-1)
        for ch in resp.json()['data']:
            if ch.get('i') == _CHANNEL_ID:
                return _decrypt_gcm(ch['s'][0])
    except Exception:
        pass
    return _URL_LIVE_FALLBACK


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    return resolver_proxy.get_stream_with_quality(plugin, _get_live_url())
