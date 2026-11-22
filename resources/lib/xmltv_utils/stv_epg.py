# -*- coding: utf-8 -*-
# This file is part of Catch-up TV & More
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

"""EPG of STV Player channels (e.g. the Great! channels), straight from STV's own API.

Programmes are returned in the same (raw) format as ``xmltv.elem_to_programme()``.
"""

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pytz
import urlquick

SCHEDULE_URL = 'https://player.stv.tv/api/schedule'
API_DT_FMT = '%Y-%m-%d %H:%M:%S'
XMLTV_DT_FMT = '%Y%m%d%H%M%S'
TIMEOUT = (3.5, 7)
CACHE_TIME = 3600


def _parse_dt(value):
    """Convert an ISO-8601 string like 2026-11-22T12:46:06+0000 to a XMLTV UTC string."""
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z').astimezone(pytz.UTC).strftime(XMLTV_DT_FMT)


def _fetch_channel(args):
    xmltv_id, channel, start, end = args
    try:
        resp = urlquick.get(SCHEDULE_URL,
                            params={'channel': channel,
                                    'startTime': '<=' + end.strftime(API_DT_FMT),
                                    'endTime': '>=' + start.strftime(API_DT_FMT),
                                    'orderBy': 'startTime',
                                    'limit': 100},
                            timeout=TIMEOUT,
                            max_age=CACHE_TIME)
        assets = json.loads(resp.content)['assets']
    except Exception:
        return []

    programmes = []
    for asset in assets:
        try:
            programme = {
                'channel': xmltv_id,
                'start': _parse_dt(asset['startTime']),
                'stop': _parse_dt(asset['endTime']),
                'title': [(asset['title'], '')],
            }
        except (KeyError, ValueError):
            continue
        if asset.get('summary'):
            programme['desc'] = [(asset['summary'].strip(), '')]
        programmes.append(programme)
    return programmes


def get_programmes(channel_ids, start, end):
    """Return the raw programmes of channels between two UTC datetimes.

    Args:
        channel_ids (dict): Key: xmltv id, value: STV channel id
    """
    if not channel_ids:
        return []
    jobs = [(xid, cid, start, end) for xid, cid in channel_ids.items()]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = pool.map(_fetch_channel, jobs)
    return [p for chan_programmes in results for p in chan_programmes]
