# -*- coding: utf-8 -*-
# This file is part of Catch-up TV & More
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

"""EPG of Channel 5 FAST channels, straight from Channel 5's own API.

These channels are not part of the XMLTV files provided by the xmltv repository,
so their programmes are fetched here and returned in the same (raw) format as
``xmltv.elem_to_programme()``.
"""

import datetime
import json
from concurrent.futures import ThreadPoolExecutor

import pytz
import urlquick

EPG_URL = 'https://corona.channel5.com/channels/{}/epg.json'
API_DT_FMT = '%Y-%m-%dT%H:%M:%S.000Z'
XMLTV_DT_FMT = '%Y%m%d%H%M%S'
TIMEOUT = (3.5, 7)
CACHE_TIME = 3600


def _parse_dt(value):
    """Convert an ISO-8601 string with offset to a XMLTV UTC string."""
    dt = datetime.datetime.fromisoformat(value)
    return dt.astimezone(pytz.UTC).strftime(XMLTV_DT_FMT)


def _fetch_channel(args):
    xmltv_id, channel_id, start, end = args
    try:
        resp = urlquick.get(EPG_URL.format(channel_id),
                            params={'start': start.strftime(API_DT_FMT),
                                    'end': end.strftime(API_DT_FMT),
                                    'platform': 'my5desktop'},
                            timeout=TIMEOUT,
                            max_age=CACHE_TIME)
        transmissions = json.loads(resp.content)['transmissions']
    except Exception:
        return []

    programmes = []
    for tr in transmissions:
        try:
            programme = {
                'channel': xmltv_id,
                'start': _parse_dt(tr['start']),
                'stop': _parse_dt(tr['end']),
                'title': [(tr['showTitle'], '')],
            }
        except (KeyError, ValueError):
            continue
        episode_title = tr.get('episodeTitle')
        if episode_title and episode_title != tr['showTitle']:
            programme['sub-title'] = [(episode_title, '')]
        if tr.get('description'):
            programme['desc'] = [(tr['description'].strip(), '')]
        if tr.get('showGenre'):
            programme['category'] = [(tr['showGenre'], '')]
        programmes.append(programme)
    return programmes


def get_programmes(channel_ids, start, end):
    """Return the raw programmes of channels between two datetimes.

    Args:
        channel_ids (dict): Key: xmltv id, value: Channel 5 channel id
        start (datetime.datetime): UTC start of the range
        end (datetime.datetime): UTC end of the range
    Returns:
        list: Programme dicts, in the format of ``xmltv.elem_to_programme()``
    """
    if not channel_ids:
        return []
    jobs = [(xid, cid, start, end) for xid, cid in channel_ids.items()]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = pool.map(_fetch_channel, jobs)
    return [p for chan_programmes in results for p in chan_programmes]
