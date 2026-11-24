# -*- coding: utf-8 -*-
# This file is part of Catch-up TV & More
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

"""EPG of the live channels of vod.tvp.pl, straight from TVP's own API.

Programmes are returned in the same (raw) format as ``xmltv.elem_to_programme()``.
"""

import json
from datetime import datetime

import pytz
import urlquick

PROGRAMMES_URL = 'https://vod.tvp.pl/api/products/lives/programmes'
API_DT_FMT = '%Y-%m-%dT%H:%M%z'
XMLTV_DT_FMT = '%Y%m%d%H%M%S'
TIMEOUT = (3.5, 15)
CACHE_TIME = 3600


def _parse_dt(value):
    """Convert an ISO-8601 string like 2026-11-22T12:10:00+01:00 to a XMLTV UTC string."""
    return datetime.fromisoformat(value).astimezone(pytz.UTC).strftime(XMLTV_DT_FMT)


def get_programmes(channel_ids, start, end):
    """Return the raw programmes of channels between two UTC datetimes.

    Args:
        channel_ids (dict): Key: xmltv id, value: vod.tvp.pl live id (both are the same number)
    """
    if not channel_ids:
        return []
    by_live_id = {str(cid): xid for xid, cid in channel_ids.items()}
    try:
        resp = urlquick.get(PROGRAMMES_URL,
                            params={'liveId[]': list(by_live_id),
                                    'since': start.astimezone(pytz.UTC).strftime(API_DT_FMT),
                                    'till': end.astimezone(pytz.UTC).strftime(API_DT_FMT),
                                    'lang': 'PL',
                                    'platform': 'BROWSER'},
                            timeout=TIMEOUT,
                            max_age=CACHE_TIME)
        data = json.loads(resp.content)
    except Exception:
        return []
    if not isinstance(data, list):
        return []

    programmes = []
    for item in data:
        try:
            xmltv_id = by_live_id[str(item['live']['id'])]
            programme = {
                'channel': xmltv_id,
                'start': _parse_dt(item['since']),
                'stop': _parse_dt(item['till']),
                'title': [(item['title'], '')],
            }
        except (KeyError, TypeError, ValueError):
            continue
        desc = item.get('description') or item.get('lead')
        if desc:
            programme['desc'] = [(desc.strip(), '')]
        genres = [g['name'] for g in item.get('genres') or [] if g.get('name')]
        if genres:
            programme['category'] = [(g, '') for g in genres]
        programmes.append(programme)
    return programmes
