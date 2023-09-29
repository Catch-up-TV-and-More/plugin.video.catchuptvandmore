# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

import json
import urlquick

from codequick import Resolver

from resources.lib import web_utils

# Live
URL_LIVE = {
    'tvpabc': 'https://krainaabc.tvp.pl/sess/TVPlayer2/api.php?@method=getTvpConfig&@callback=__anthill_jsonp_442__&corsHost=krainaabc.tvp.pl&id=51696812',
    'tvpabc2': 'https://krainaabc.tvp.pl/sess/TVPlayer2/api.php?@method=getTvpConfig&@callback=__anthill_jsonp_401__&corsHost=krainaabc.tvp.pl&id=57181933'
}

@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    resp = urlquick.get(URL_LIVE[item_id],
                        headers={'User-Agent': web_utils.get_random_ua()},
                        max_age=-1, timeout=30)
    print('newresp=', resp.text)

    # extract json content from jsonp reply
    resp_json_body = resp.text.split("(", 1)[1]
    resp_json_body = resp_json_body[:1 + resp_json_body.rfind("}")]
    # parse json
    resp_json = json.loads(resp_json_body)

    video_files = resp_json.get('content').get('files')
    for video_file in video_files:
        if 'hls' == video_file.get('type'):
            return video_file.get('url')
    default_url = video_files[0].get('url')
    if default_url is not None:
        return default_url

    return False
