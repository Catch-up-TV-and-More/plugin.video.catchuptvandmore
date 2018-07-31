# -*- coding: utf-8 -*-

import requests
import json


# POST data:b
# value = {"action": "infinite_scroll", "scripts[]": "jquery-core", "scripts[]": "jquery-migrate", "scripts[]": "jquery", "page": "1", "query_args[order]": "DESC", "query_args[posts_per_page]": "6", "order": "DESC", "query_args[category_name]": "ecologie", "currentday": "12.06.18"}
headers_value = {'Content-type': 'application/json', 'Connection': 'keep-alive', 'Content-Length': '784'}
url = 'https://media-services-public.vrt.be/vualto-video-aggregator-web/rest/external/v1/tokens'

# print 'payload : ' + json.dumps(value)
print 'headers : ' + json.dumps(headers_value)
print 'url : ' + url

# r = requests.post(url, data = json.dumps(value), headers = headers_value)
r = requests.post(url)
print 'Reponse : ' + r.text
print 'status : ' + str(r.status_code)

token = json.loads(r.text)


