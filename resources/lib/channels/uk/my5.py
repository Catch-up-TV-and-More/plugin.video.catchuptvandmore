# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Joaopa
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

# with contributions by 
#    nictjir, joaopa00, berkhornet

from __future__ import unicode_literals

import re
import json
import base64
from base64 import urlsafe_b64decode
import xbmc
import urlquick
import urllib
import time

import os
import xbmcvfs

#from kodi_six import xbmcgui
from codequick import Listitem, Resolver, Route
#import urlquick

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


try:
    from Crypto.Cipher import AES
except ImportError:
    from Cryptodome.Cipher import AES

try:
    from Crypto.Util.Padding import unpad
except ImportError:
    from Cryptodome.Util.Padding import unpad

try:
    from Crypto.Hash import HMAC, SHA256
except ImportError:
    from Cryptodome.Hash import HMAC, SHA256

from resources.lib.kodi_utils import get_kodi_version, get_selected_item_art, get_selected_item_label, get_selected_item_info, INPUTSTREAM_PROP
from resources.lib.menu_utils import item_post_treatment

from resources.lib import resolver_proxy, web_utils
from resources.lib.resolver_proxy import get_stream_with_quality


# Local HTTP server to mangle live fetched mpd
LOCAL_URL = 'http://127.0.0.1:5057/5LIVE'

CORONA_URL = 'https://corona.channel5.com/shows/'
BASIS_URL = CORONA_URL + '%s/seasons'

URL_SEASONS = BASIS_URL + '.json'
URL_EPISODES = BASIS_URL + '/%s/episodes.json'
FEEDS_API = 'https://feeds-api.channel5.com/collections/%s/concise.json'

URL_VIEW_ALL = CORONA_URL + 'search.json'
URL_WATCHABLE = 'https://corona.channel5.com/watchables/search.json'
URL_SHOWS = 'https://corona.channel5.com/shows/search.json'
IMG_URL = 'https://api-images.channel5.com/otis/images/episode/%s/320x180.jpg'
SHOW_IMG_URL = 'https://api-images.channel5.com/otis/images/show/%s/320x180.jpg'


ONEOFF = 'https://corona.channel5.com/shows/%s/episodes/next.json'


GENERIC_HEADERS = {"User-Agent": web_utils.get_random_ua()}

LICC_URL = 'https://cassie.channel5.com/api/v2/media/my5desktopng/%s.json?timestamp=%s'
LIVE_LICC_URL = 'https://cassie.channel5.com/api/v2/live_media/my5desktopng/%s.json?timestamp=%s'
KEYURL = "https://player.akamaized.net/html5player/core/html5-c5-player.js"
CERT_URL = 'https://c5apps.channel5.com/wv/c5-wv-app-cert-20170524.bin'

HOME              = xbmcvfs.translatePath('special://home/')
ADDONS            = os.path.join(HOME,     'addons')
RESOURCE_IMAGES   = os.path.join(ADDONS,   'resource.images.catchuptvandmore')
RESOURCES         = os.path.join(RESOURCE_IMAGES,   'resources')
CHANNELS          = os.path.join(RESOURCES,         'channels')
UK_CHANNELS       = os.path.join(CHANNELS,          'uk')
fanartpath        = os.path.join(UK_CHANNELS,       'my5_fanart.jpg')
iconpath          = os.path.join(UK_CHANNELS,       'my5.png')

feeds_api_params = {
    'vod_available': 'my5desktop',
    'friendly': '1'
}

view_api_params = {
    'platform': 'my5desktop',
    'friendly': '1'
}

lic_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0',
        'Referer': 'https://www.channel5.com/',
        'Content-Type': '',
    }




# susbstitute some characters in auth string before requesting license
def change(auth):
    result = ''.join(str(x) for x in auth)
    result = result.replace("+", "-")
    result = result.replace("/", "_")
    result = re.sub(r'=={0,}$', '', result)
    return(result)

# all we need is array of ascii value of each character in the long story 
def url_parse(queryStr):
    unicodestring=urllib.parse.unquote(queryStr)
    return [ord(c) for c in unicodestring]



def getdata(ui,watching):
   # We need 2 things from the js file, the long string of gibberish and the short
   # string to OR with,
   # I assume short string is always 6 digits long to regexp search on
   # The lomg string is really long so i look for at least 3000 characters

   resp = urlquick.get(KEYURL)
   content = resp.content.decode("utf-8", "ignore")

   # short string
   m = re.compile(r';}}}\)\(\'(......)\'\)};').search(content)
   ss = m.group(1)
   # long string
   m = re.compile(r'\(\){return "(.{3000,})";\}').search(content)
   s = str(m.group(1))


   z = url_parse(s)
   l = len(z)

   y = 0
   sout = ""

   for x in range(l):
       if (y > 5):
         y = 0
       p1 = z[x]
       p2 = ord(ss[y])
       k = p1 ^ p2
       # Only worried about printable characters for what we need
       if ( (k > 31) and (k < 127) ):
        sout = sout + chr(k)
       y = y + 1

   #extract the key from sout
   m = re.compile(r'SSL_MA..(.{24})..(.{24})').search(sout)
   k1 = m.group(1)
   k2 = m.group(2)


   # we need an 8 byte array that makes magic
   m = re.compile(r'2689\)\]=\[(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\]').search(content)

   timeStamp = str( int(time.time()) ) 

   
   if (watching == "vod"): 
      CALL_URL = LICC_URL % (ui, timeStamp)
   else:
      CALL_URL = LIVE_LICC_URL % (ui, timeStamp)

   h = HMAC.new(base64.urlsafe_b64decode(k1),digestmod=SHA256)
   h.update(bytes(CALL_URL,encoding="utf-8"))

   webSafeAuthKey=str(base64.urlsafe_b64encode(h.digest()))
   #Strip out the padding -- two chars on each side: "b'....='" 
   LICFULL_URL = CALL_URL + "&auth=" + change(webSafeAuthKey[2:-2])
   return (LICFULL_URL, k2)

def ivdata(URL):
    resp = urlquick.get(URL, headers=GENERIC_HEADERS)
    root = json.loads(resp.text)
    iv = root['iv']
    data = root['data']
    return(iv, data)



# For Iv and Data processing


def mangle(st):
    result = st
    result = result.replace("-", "+")
    result = result.replace("_", "/")
    return (result)


def getUseful(s):
    # back to json parsing to also do live urls .....
    keyserver = 'NA'
    streamUrl ='NA'
    subtitile = 'NA'
    data = json.loads(s)
    jsonData = data['assets']
    for x in jsonData:
      if (x['drm'] == "widevine" ):
        keyserver = (x['keyserver'])
        u = (x['renditions'])
        for i in u:
          streamUrl = i['url']

    return  (streamUrl, keyserver, subtitile)

         

def padAndB64(data, length=16):
    data=base64.b64decode(data)
    paddingToUse = b'\x00'*(length-len(data))
    #Undoubtedly there is a better way of doing null byte padding, but it's not in the padding routines...
    return data+paddingToUse

def part2(iv, aesKey, rdata):
    realIv = padAndB64(mangle(iv))
    realAesKey = padAndB64(mangle(aesKey))
    realRData = base64.b64decode(mangle(rdata))
    cipher = AES.new(realAesKey, AES.MODE_CBC, iv=realIv)
    dataToParse=unpad(cipher.decrypt(realRData),16)
    (stream, drmurl, sub) = getUseful(dataToParse.decode('utf-8'))
    return (stream, drmurl, sub)



@Route.register
def list_categories(plugin, **kwargs):
    resp = urlquick.get(FEEDS_API % 'PLC_My5SubGenreBrowsePageSubNav', headers=GENERIC_HEADERS, params=feeds_api_params)
    root = json.loads(resp.text)
    for i in range(int(root['total_items'])):
     try:
        item = Listitem()
        item_id = 1
        item.label = root['filters']['contents'][i]['title']
        browse_name = root['filters']['contents'][i]['id']
        offset = "0"
        item.set_callback(list_subcategories, item_id=item_id, browse_name=browse_name, offset=offset)
        item_post_treatment(item)
        item.art["thumb"] = iconpath
        item.art["fanart"] = fanartpath
        yield item
     except:
        pass


@Route.register
def list_subcategories(plugin, item_id, browse_name, offset, **kwargs):
    if (browse_name == "PLC_My5AllShows"):
       watchable_params = '?limit=25&offset=%s&platform=my5desktop&friendly=1' % str(offset)
       s = URL_SHOWS + watchable_params
       resp = urlquick.get(s, headers=GENERIC_HEADERS, params=feeds_api_params)
       root = json.loads(resp.text)
       item_number = int(root['size'])
       for emission in root['shows']:
        try:
         standalone = emission['standalone']
         standalone = "yes"
        except:
         standalone = "no"

        if (standalone == "yes"):
         item = Listitem()
         item.label = emission['title']
         item.info['plot'] = emission['s_desc']
         fname = emission['f_name']
         picture_id = emission['id']
         item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
         item.set_callback(get_video_url, item_id=item_id, fname=fname, season_f_name="", show_id="show_id", standalone="yes")
         item_post_treatment(item)
         yield item

        else:
         try:
          item = Listitem()
          title = emission['title']
          item.label = title
          item.info['plot'] = emission['s_desc']
          fname = emission['f_name']
          picture_id = emission['id']
          item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
          item.set_callback(list_seasons, item_id=item_id, fname=fname, pid=picture_id, title=title)
          item_post_treatment(item)
          yield item
         except:
          pass

       if 'next_page_url' in root:
          offset = str(int(offset) + int(root['limit']))
          yield Listitem.next_page(item_id=item_id, browse_name=browse_name, offset=offset)


    else:
       resp = urlquick.get(FEEDS_API % browse_name, headers=GENERIC_HEADERS, params=feeds_api_params)
       root = json.loads(resp.text)
       item_number = int(root['total_items'])

       if root['filters']['type'] == 'Collection':
         offset = 0
         for i in range(item_number):
          try:
            item = Listitem()
            item.label = root['filters']['contents'][i]['title']
            browse_name = root['filters']['contents'][i]['id']
            item.set_callback(list_collections, item_id=item_id, browse_name=browse_name, offset=offset)
            item_post_treatment(item)
            item.art["thumb"] = iconpath
            item.art["fanart"] = fanartpath
            yield item
          except:
            pass
       elif root['filters']['type'] == 'Show':
        ids = root['filters']['ids']
        watchable_params = '?limit=%s&offset=0s&platform=my5desktop&friendly=1' % str(item_number)
        for i in range(item_number):
          try:
            watchable_params = watchable_params + '&ids[]=%s' % ids[i]
          except:
            pass


        resp = urlquick.get(URL_SHOWS + watchable_params, headers=GENERIC_HEADERS)
        root = json.loads(resp.text)
        for watchable in root['shows']:
          try:
            item = Listitem()
            item.label = watchable['title']
            item.info['plot'] = watchable['s_desc']
            item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % watchable['id']
            show_id = watchable['id']
            fname = watchable['f_name']
            item.set_callback(get_video_url, item_id=item_id, fname=fname, season_f_name="season_f_name", show_id=show_id, standalone="yes")
            item_post_treatment(item)
            yield item
          except:
            pass


       elif root['filters']['type'] == 'Watchable':
        ids = root['filters']['ids']
        watchable_params = '?limit=%s&offset=0s&platform=my5desktop&friendly=1' % str(item_number)
        for i in range(item_number):
          try:
            watchable_params = watchable_params + '&ids[]=%s' % ids[i]
          except:
            pass
        resp = urlquick.get(URL_WATCHABLE + watchable_params, headers=GENERIC_HEADERS)
        root = json.loads(resp.text)

        for watchable in root['watchables']:
          try:
            item = Listitem()
            item.label = watchable['sh_title']
            item.info['plot'] = watchable['s_desc']
            t = int(int(watchable['len']) // 1000)
            item.info['duration'] = t
            item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % watchable['sh_id']
            #fname = watchable['f_name']
            #season_f_name = watchable['sea_f_name']
            show_id = watchable['id']
            item.set_callback(get_video_url, item_id=item_id, fname="fname", season_f_name="season_f_name", show_id=show_id, standalone="no")
            item_post_treatment(item)
            yield item
          except:
            pass



@Route.register
def list_watchables(plugin, itemid, browse_name, offset, item_number, ids):
    return False


@Route.register
def list_collections(plugin, item_id, browse_name, offset, **kwargs):
    resp = urlquick.get(FEEDS_API % browse_name, headers=GENERIC_HEADERS, params=feeds_api_params)
    root = json.loads(resp.text)
    subgenre = root['filters']['vod_subgenres']
    view_all_params = {
        'platform': 'my5desktop',
        'friendly': '1',
        'limit': '25',
        'offset': offset,
        'vod_subgenres[]': subgenre
    }
    resp = urlquick.get(URL_VIEW_ALL, headers=GENERIC_HEADERS, params=view_all_params)
    root = json.loads(resp.text)

    for emission in root['shows']:
      try:
        standalone = emission['standalone']
        standalone = "yes"
      except:
        standalone = "no"

      if (standalone == "yes"):
        item = Listitem()
        item.label = emission['title']
        item.info['plot'] = emission['s_desc']
        fname = emission['f_name']
        picture_id = emission['id']
        item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
        item.set_callback(get_video_url, item_id=item_id, fname=fname, season_f_name="", show_id="show_id", standalone="yes")
        item_post_treatment(item)
        yield item

      else:
       try:
        item = Listitem()
        title = emission['title']
        item.label = title
        item.info['plot'] = emission['s_desc']
        fname = emission['f_name']
        picture_id = emission['id']
        item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
        item.set_callback(list_seasons, item_id=item_id, fname=fname, pid=picture_id, title=title)
        item_post_treatment(item)
        yield item
       except:
        pass




    if 'next_page_url' in root:
        offset = str(int(offset) + int(view_all_params['limit']))
        yield Listitem.next_page(item_id=item_id, browse_name=browse_name, offset=offset)


@Route.register
def list_seasons(plugin, item_id, fname, pid, title, **kwargs):


    resp = urlquick.get(URL_SEASONS % fname, headers=GENERIC_HEADERS, params=view_api_params)
    if resp.ok:
        root = json.loads(resp.text)

        for season in root['seasons']:
          try:
            item = Listitem()
            season_number = season['seasonNumber']
            item.label = title + '\nSeason ' + season_number
            picture_id = pid
            item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
            item.set_callback(list_episodes, item_id=item_id, fname=fname, season_number=season_number)
            item_post_treatment(item)
            yield item
          except:
            pass


@Route.register
def list_episodes(plugin, item_id, fname, season_number, **kwargs):
    resp = urlquick.get(URL_EPISODES % (fname, season_number), headers=GENERIC_HEADERS, params=view_api_params)
    root = json.loads(resp.text)

    for episode in root['episodes']:
      try:
        item = Listitem()
        picture_id = episode['id']
        item.art['thumb'] = item.art['landscape'] = IMG_URL % picture_id
        item.label = episode['title']
        item.info['plot'] = episode['s_desc']
        t = int(int(episode['len']) // 1000)
        item.info['duration'] = t
        season_f_name = episode['sea_f_name']
        fname = episode['f_name']
        show_id = episode['id']
        item.set_callback(get_video_url, item_id=item_id, fname=fname, season_f_name=season_f_name, show_id=show_id, standalone="no")
        item_post_treatment(item)
        yield item
      except:
        pass


@Resolver.register
def get_video_url(plugin, item_id, fname, season_f_name, show_id, standalone, **kwargs):

    # for a onceoff/stanalone we still dont have showid so we get it now
    if (standalone == "yes"):
      resp = urlquick.get(ONEOFF % fname, headers=GENERIC_HEADERS, params=view_api_params)
      if resp.ok:
        root = json.loads(resp.text)
        try:
          show_id = root['id']
        except:
          pass


    LICFULL_URL, aesKey  = getdata(show_id, "vod")
    (iv,data)=ivdata(LICFULL_URL)
    (stream,drmurl,suburl) = part2(iv,aesKey,data)
    xbmc.log("Stream : %s" % stream, level=xbmc.LOGERROR)
    xbmc.log("Licensce :  %s" % drmurl, level=xbmc.LOGERROR)

    # get server certiticate data and b64 it
    resp = urlquick.get(CERT_URL)
    content = resp.content
    cert_data = (base64.b64encode(content)).decode('ascii')

    stream_headers = urlencode(lic_headers)
    license_url = '%s|%s|R{SSM}|' % (drmurl, stream_headers)


    item = Listitem()
    item.path = stream
    item.label = get_selected_item_label()
    item.art.update(get_selected_item_art())
    item.info.update(get_selected_item_info())
    item.property[INPUTSTREAM_PROP] = 'inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property[ 'inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property[ 'inputstream.adaptive.server_certificate'] = cert_data
    item.property['inputstream.adaptive.license_key'] = license_url
    return item
    
@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    LICFULL_URL, aesKey  = getdata(item_id,"live")
    (iv,data)=ivdata(LICFULL_URL)
    (stream,drmurl,suburl) = part2(iv,aesKey,data)

    # Send request to local web server

    # get server certiticate data and b64 it
    resp = urlquick.get(CERT_URL)
    content = resp.content
    cert_data = (base64.b64encode(content)).decode('ascii')

    stream_headers = urlencode(lic_headers)
    license_url = '%s|%s|R{SSM}|' % (drmurl, stream_headers)


    item = Listitem()
    item.path = stream
    item.label = get_selected_item_label()
    item.art.update(get_selected_item_art())
    item.info.update(get_selected_item_info())
    item.property[INPUTSTREAM_PROP] = 'inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property[ 'inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property[ 'inputstream.adaptive.server_certificate'] = cert_data
    item.property['inputstream.adaptive.license_key'] = license_url
    return item


