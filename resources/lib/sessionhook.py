# -*- coding: utf-8 -*-
# Copyright: (c) JUL1EN094, SPM, SylvainCecchetto
# Copyright: (c) 2016, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

#
# ref. https://lukasa.co.uk/2017/02/Configuring_TLS_With_Requests/
#
import ssl
import requests
from requests.adapters import HTTPAdapter
from requests.sessions import Session
from requests.packages.urllib3.util.ssl_ import create_urllib3_context


class DESAdapter(HTTPAdapter):
    """
    A TransportAdapter that re-enables 3DES support in Requests.
    """
    def __init__(self, *args, **kwargs):
        self.ssl_context = kwargs.pop('ssl_context', None)
        self.ecdhCurve = kwargs.pop('ecdhCurve', 'prime256v1')

        if not self.ssl_context:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            self.ssl_context.set_ecdh_curve(self.ecdhCurve)

        super(DESAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super(DESAdapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super(DESAdapter, self).proxy_manager_for(*args, **kwargs)


class SessionHook(Session):
    def __init__(self, *args, **kwargs):
        self.debug = kwargs.pop('debug', False)

        super(SessionHook, self).__init__(*args, **kwargs)

        self.mount(
            'https://',
            DESAdapter()
        )
