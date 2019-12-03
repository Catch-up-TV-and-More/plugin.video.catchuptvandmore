"""
xmltv.py - Python interface to XMLTV format, based on XMLTV.pm

Copyright (C) 2001 James Oakley <jfunk@funktronics.ca>

This library is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along
with this software; if not, see <http://www.gnu.org/licenses/>.
"""

# Stolen from https://bitbucket.org/jfunk/python-xmltv/src/default/xmltv.py

import os
import pytz
import datetime
from tzlocal import get_localzone
from zipfile import ZipFile

from xml.etree.ElementTree import ElementTree

from kodi_six import xbmcvfs

from codequick import Script, storage
import urlquick

from resources.lib.common import current_timestamp

# The Python-XMLTV version
VERSION = "1.4.3"

# The date format used in XMLTV (the %Z will go away in 0.6)
date_format = '%Y%m%d%H%M%S %Z'
date_format_notz = '%Y%m%d%H%M%S'


def set_attrs(d, elem, attrs):
    """
    set_attrs(d, elem, attrs) -> None

    Add any attributes in 'attrs' found in 'elem' to 'd'
    """
    for attr in attrs:
        if attr in elem.keys():
            d[attr] = elem.get(attr)


def set_boolean(d, name, elem):
    """
    set_boolean(d, name, elem) -> None

    If element, 'name' is found in 'elem', set 'd'['name'] to a boolean
    from the 'yes' or 'no' content of the node
    """
    node = elem.find(name)
    if node is not None:
        if node.text.lower() == 'yes':
            d[name] = True
        elif node.text.lower() == 'no':
            d[name] = False


def append_text(d, name, elem, with_lang=True):
    """
    append_text(d, name, elem, with_lang=True) -> None

    Append any text nodes with 'name' found in 'elem' to 'd'['name']. If
    'with_lang' is 'True', a tuple of ('text', 'lang') is appended
    """
    for node in elem.findall(name):
        if name not in d.keys():
            d[name] = []
        if with_lang:
            d[name].append((node.text, node.get('lang', '')))
        else:
            d[name].append(node.text)


def set_text(d, name, elem, with_lang=True):
    """
    set_text(d, name, elem, with_lang=True) -> None

    Set 'd'['name'] to the text found in 'name', if found under 'elem'. If
    'with_lang' is 'True', a tuple of ('text', 'lang') is set
    """
    node = elem.find(name)
    if node is not None:
        if with_lang:
            d[name] = (node.text, node.get('lang', ''))
        else:
            d[name] = node.text


def append_icons(d, elem):
    """
    append_icons(d, elem) -> None

    Append any icons found under 'elem' to 'd'
    """
    for iconnode in elem.findall('icon'):
        if 'icon' not in d.keys():
            d['icon'] = []
        icond = {}
        set_attrs(icond, iconnode, ('src', 'width', 'height'))
        d['icon'].append(icond)


def elem_to_channel(elem):
    """
    elem_to_channel(Element) -> dict

    Convert channel element to dictionary
    """
    d = {'id': elem.get('id'),
         'display-name': []}

    append_text(d, 'display-name', elem)
    append_icons(d, elem)
    append_text(d, 'url', elem, with_lang=False)

    return d


def read_channels(fp=None, tree=None):
    """
    read_channels(fp=None, tree=None) -> list

    Return a list of channel dictionaries from file object 'fp' or the
    ElementTree 'tree'
    """
    if fp:
        et = ElementTree()
        tree = et.parse(fp)
    return [elem_to_channel(elem) for elem in tree.findall('channel')]


def elem_to_programme(elem):
    """
    elem_to_programme(Element) -> dict

    Convert programme element to dictionary
    """
    d = {'start': elem.get('start'),
         'channel': elem.get('channel'),
         'title': []}

    set_attrs(d, elem, ('stop', 'pdc-start', 'vps-start', 'showview',
                        'videoplus', 'clumpidx'))

    append_text(d, 'title', elem)
    append_text(d, 'sub-title', elem)
    append_text(d, 'desc', elem)

    crednode = elem.find('credits')
    if crednode is not None:
        creddict = {}
        # TODO: actor can have a 'role' attribute
        for credtype in ('director', 'actor', 'writer', 'adapter', 'producer',
                         'presenter', 'commentator', 'guest', 'composer',
                         'editor'):
            append_text(creddict, credtype, crednode, with_lang=False)
        d['credits'] = creddict

    set_text(d, 'date', elem, with_lang=False)
    append_text(d, 'category', elem)
    set_text(d, 'language', elem)
    set_text(d, 'orig-language', elem)

    lennode = elem.find('length')
    if lennode is not None:
        lend = {'units': lennode.get('units'),
                'length': lennode.text}
        d['length'] = lend

    append_icons(d, elem)
    append_text(d, 'url', elem, with_lang=False)
    append_text(d, 'country', elem)

    for epnumnode in elem.findall('episode-num'):
        if 'episode-num' not in d.keys():
            d['episode-num'] = []
        d['episode-num'].append((epnumnode.text,
                                 epnumnode.get('system', 'xmltv_ns')))

    vidnode = elem.find('video')
    if vidnode is not None:
        vidd = {}
        for name in ('present', 'colour'):
            set_boolean(vidd, name, vidnode)
        for videlem in ('aspect', 'quality'):
            venode = vidnode.find(videlem)
            if venode is not None:
                vidd[videlem] = venode.text
        d['video'] = vidd

    audnode = elem.find('audio')
    if audnode is not None:
        audd = {}
        set_boolean(audd, 'present', audnode)
        stereonode = audnode.find('stereo')
        if stereonode is not None:
            audd['stereo'] = stereonode.text
        d['audio'] = audd

    psnode = elem.find('previously-shown')
    if psnode is not None:
        psd = {}
        set_attrs(psd, psnode, ('start', 'channel'))
        d['previously-shown'] = psd

    set_text(d, 'premiere', elem)
    set_text(d, 'last-chance', elem)

    if elem.find('new') is not None:
        d['new'] = True

    for stnode in elem.findall('subtitles'):
        if 'subtitles' not in d.keys():
            d['subtitles'] = []
        std = {}
        set_attrs(std, stnode, ('type',))
        set_text(std, 'language', stnode)
        d['subtitles'].append(std)

    for ratnode in elem.findall('rating'):
        if 'rating' not in d.keys():
            d['rating'] = []
        ratd = {}
        set_attrs(ratd, ratnode, ('system',))
        set_text(ratd, 'value', ratnode, with_lang=False)
        append_icons(ratd, ratnode)
        d['rating'].append(ratd)

    for srnode in elem.findall('star-rating'):
        if 'star-rating' not in d.keys():
            d['star-rating'] = []
        srd = {}
        set_attrs(srd, srnode, ('system',))
        set_text(srd, 'value', srnode, with_lang=False)
        append_icons(srd, srnode)
        d['star-rating'].append(srd)

    for revnode in elem.findall('review'):
        if 'review' not in d.keys():
            d['review'] = []
        rd = {}
        set_attrs(rd, revnode, ('type', 'source', 'reviewer',))
        set_text(rd, 'value', revnode, with_lang=False)
        d['review'].append(rd)

    return d


def read_programmes(fp=None, tree=None):
    """
    read_programmes(fp=None, tree=None) -> list

    Return a list of programme dictionaries from file object 'fp' or the
    ElementTree 'tree'
    """
    if fp:
        et = ElementTree()
        tree = et.parse(fp)
    return [elem_to_programme(elem) for elem in tree.findall('programme')]


def date_str_to_timestamp(s):
    # ATM, only telerama format is supported (%Y%m%d%H%M%S %Z)

    # Remove timezone part to get %Y%m%d%H%M%S format
    s = s.split(' ')[0]

    # Get the naive datetime object
    d = datetime.datetime.strptime(s, date_format_notz)

    # Add telerama timezone
    telerama_tz = pytz.timezone('Europe/Paris')
    d = telerama_tz.localize(d)

    # Convert to UTC timezone
    utc_tz = pytz.UTC
    d = d.astimezone(utc_tz)

    # epoch is the beginning of time in the UTC timestamp world
    epoch = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=utc_tz)

    # get the total second difference
    ts = (d - epoch).total_seconds()

    return ts


def read_current_programmes(fp=None, tree=None):
    """
    read_programmes(fp=None, tree=None) -> list

    Return a list of programme dictionaries from file object 'fp' or the
    ElementTree 'tree'
    """
    if fp:
        et = ElementTree()
        tree = et.parse(fp)
    programmes = []
    for elem in tree.findall('programme'):
        start_s = elem.get('start')
        stop_s = elem.get('stop')

        start_ts = date_str_to_timestamp(start_s)
        stop_ts = date_str_to_timestamp(stop_s)

        current_ts = current_timestamp()
        if current_ts >= start_ts and current_ts <= stop_ts:
            programmes.append(elem_to_programme(elem))
    return programmes


def read_data(fp=None, tree=None):
    """
    read_data(fp=None, tree=None) -> dict

    Get the source and other info from file object fp or the ElementTree
    'tree'
    """
    if fp:
        et = ElementTree()
        tree = et.parse(fp)

    d = {}
    set_attrs(d, tree, ('date', 'source-info-url', 'source-info-name',
                        'source-data-url', 'generator-info-name',
                        'generator-info-url'))
    return d


xmtlv_zip_urls = {
    'fr_live': 'https://github.com/Catch-up-TV-and-More/xmltv/raw/master/tv_guide_fr_lite.zip',
    'be_live': 'https://github.com/Catch-up-TV-and-More/xmltv/raw/master/tv_guide_be_lite.zip'
}

xmtlv_filenames = {
    'fr_live': 'tv_guide_fr_lite.xml',
    'be_live': 'tv_guide_be_lite.xml'
}


def programme_post_treatment(programme):
    for k in ['title', 'desc']:
        if k in programme:
            s = ''
            for t in programme[k]:
                s = s + t[0] + ' - '
            s = s[:-3]
            programme[k] = s

    if 'icon' in programme:
        programme['icon'] = programme['icon'][0]['src']

    if 'length' in programme:
        programme['length'] = int(programme['length']['length']) * 60

    # For start and stop we use a string in %Hh%m format

    # Get start and stop in UTC timestamp
    start_ts = date_str_to_timestamp(programme['start'])
    stop_ts = date_str_to_timestamp(programme['stop'])

    # Get local timezone
    try:
        local_tz = get_localzone()
    except Exception:
        # Hotfix issue #102
        local_tz = pytz.timezone('Europe/Paris')

    # Convert start and stop on naive datetime object
    start_dt = datetime.datetime.utcfromtimestamp(start_ts)
    stop_dt = datetime.datetime.utcfromtimestamp(stop_ts)

    # Add UTC timezone to start and stop
    utc_tz = pytz.UTC
    start_dt = utc_tz.localize(start_dt)
    stop_dt = utc_tz.localize(stop_dt)

    # Move to our timezone
    start_dt = start_dt.astimezone(local_tz)
    stop_dt = stop_dt.astimezone(local_tz)

    programme['start'] = start_dt.strftime("%Hh%M")
    programme['stop'] = stop_dt.strftime("%Hh%M")

    return programme


def grab_tv_guide(menu_id, menu):
    xmltv_fp = os.path.join(Script.get_info('profile'), xmtlv_filenames[menu_id])
    xmltv_fp_zip = xmltv_fp + '.zip'

    # Check if we need to download a fresh xmltv file
    need_to_update_xmltv = False
    if not xbmcvfs.exists(xmltv_fp):
        Script.log('xmltv file of {} does not exist'.format(menu_id))
        need_to_update_xmltv = True
    else:
        with storage.PersistentDict('tv_guide') as db:
            if xmltv_fp not in db:
                db[xmltv_fp] = current_timestamp()
                db.flush()
            if current_timestamp() - db[xmltv_fp] > 24 * 3600:
                Script.log('xmltv file of {} need to be updated'.format(menu_id))
                need_to_update_xmltv = True
            else:
                Script.log('xmltv file of {} was already download in the last 24 hours'.format(menu_id))

    # If needed, update xmltv file
    if need_to_update_xmltv:
        Script.log('Download and extract xmltv zip file of {}'.format(menu_id))

        # Download zip file
        r = urlquick.get(xmtlv_zip_urls[menu_id])
        with open(xmltv_fp_zip, 'wb') as f:
            f.write(r.content)

        # Extract zip file
        with ZipFile(xmltv_fp_zip, 'r') as zipObj:
            zipObj.extractall(Script.get_info('profile'))

        # Remove zip file
        xbmcvfs.delete(xmltv_fp_zip)

        # Save current time for this xmltv file
        with storage.PersistentDict('tv_guide') as db:
            db[xmltv_fp] = current_timestamp()
            db.flush()

    # Grab programmes in xmltv file
    programmes = read_current_programmes(open(xmltv_fp, 'r'))

    # Use the channel as key
    tv_guide = {}
    for programme in programmes:
        programme = programme_post_treatment(programme)
        tv_guide[programme['channel']] = programme

    return tv_guide
