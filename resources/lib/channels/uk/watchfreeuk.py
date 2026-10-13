# _____________________________________________________________________________
# Copyright (c) 2025, Dimitri Kroon
# SPDX-License-Identifier: GPL-2.0-or-later
# See LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt
# This file is part of Catch-up TV & More
# _____________________________________________________________________________
import json
import re
from codecs import unicode_escape_decode

from html import unescape

from codequick import Listitem, Resolver, Route
import urlquick

from resources.lib import web_utils
from resources.lib import menu_utils
from resources.lib import resolver_proxy


DFLT_CACHE_TIME = 1200
DFLT_HEADERS = {"User-Agent": web_utils.get_random_ua()}
# Need a pretty long read timeout to accommodate search and playlist requests.
REQ_TIMEOUT = (3.5, 15)

BASE_URL = 'https://www.watchfreeuk.co.uk'


def clean_str(src_txt):
    """Strip all whitespace from every line in `src_txt` and
    combine them to a single line of text.
    """
    if src_txt is None:
        return ''
    return unescape(' '.join(t.strip() for t in src_txt.strip().split('\n')))


def check_geo_block(resp):
    """Geo-blocked requests just return normally with status 200 - OK.
    Check the page's title to determine whether it was blocked. And if it was,
    raise an error and remove the page from the cache to avoid getting the same
    error again when the user has resolved the block.

    Since this function already parses the HTML document, return the root element
    for further processing.

    """
    root = resp.parse()
    page_title = root.find('.//title')
    if page_title is None:
        # The content of sliders and search results do not have a title when it's
        # successfully returned. However, if it is geo-blocked, a regular HTML
        # page with a title tag is returned.
        return root

    title_txt = page_title.text
    if 'Service Unavailable' in title_txt:
        urlhash = urlquick.hash_url(resp.request)
        urlquick.CacheHTTPAdapter(urlquick.CACHE_LOCATION).del_cache(urlhash)
        err = urlquick.HTTPError(Route.localize(30893))
        raise err
    return root


def fetch(url, **kwargs):
    """Make a GET request to the specified `url` and return an xml tree
    that represents the HTML page

    """
    kwargs.setdefault('headers', DFLT_HEADERS)
    kwargs.setdefault('timeout', REQ_TIMEOUT)
    kwargs.setdefault('max_age', DFLT_CACHE_TIME)
    resp = urlquick.get(url, **kwargs)
    return check_geo_block(resp)


def playlist_url(component_div) -> str:
    """Build a full url to the full playlist content from several attributes of the div.

    This creates a link to the whole collection as obtained by clicking the 'more'
    button on the slider.

    """
    hx_get = component_div.get("hx-get").replace('sliders/', '').replace('seriesPlaylist/', 'series/playlist/')
    url = ''.join((BASE_URL, hx_get))
    return url


def parse_playlist_item(video_item):
    """Parse a <div> element that represents a video item.

        Scrape as much info as possible from the div and its children and return
        a codequick Listitem.

    """
    video_url = video_item.get('data-hover-href')

    play_btn = video_item.find(".//div[@class='play-button']")
    if not play_btn:
        return None

    x_data = unicode_escape_decode(play_btn.get('x-data'))[0]
    match = re.search(r"programme: JSON.parse\('([^']+)'\)", x_data, re.DOTALL)
    pgm_data = json.loads(match[1])

    item_type = pgm_data.get('type')
    uvid = pgm_data.get('uvid')
    video_img = pgm_data.get('image', '').replace('\\/', '/')
    season = int(pgm_data.get('season', 0))
    episode = int(pgm_data.get('episode', 0))

    li = Listitem()
    li.label = pgm_data.get('title')
    li.art['thumb'] = li.art['landscape'] = video_img
    li.info['plot'] = '\n'.join(x for x in (pgm_data.get('series_title'),
                                            pgm_data.get('synopsis'),
                                            ' ',
                                            f'Series {season}, Episode {episode}' if episode else None,
                                            pgm_data.get('play_warning_popup_message')) if x)
    li.info['duration'] = pgm_data.get('duration')
    if uvid and item_type == 'show':
        li.set_callback(play_vod, uvid=uvid)
    else:
        li.set_callback(list_series, url=video_url)
    menu_utils.item_post_treatment(li, is_playable=uvid is not None)
    return li


def parse_more_tile(more_tile):
    path = more_tile.get('href')
    if not path:
        return None
    li = Listitem('More')
    li.property['SpecialSort'] = 'bottom'
    li.set_callback(list_slider, url=BASE_URL + path)
    return li


@Route.register()
def main_menu(_, **__):
    yield Listitem.from_dict(
        callback=list_slider_page,
        label='Home',
        params={'url': BASE_URL + '/'}
    )
    yield Listitem.from_dict(
        callback=list_slider_page,
        label='True Crime',
        params={'url': BASE_URL + '/page/true-crime'}
    )
    yield Listitem.from_dict(
        callback=list_slider_page,
        label='Legend',
        params={'url': BASE_URL + '/page/legend'}
    )
    yield Listitem.from_dict(
        callback=list_grid_page,
        label='Series',
        params={'url': BASE_URL + '/page/series'}
    )
    yield Listitem.from_dict(
        callback=list_grid_page,
        label='Movies',
        params={'url': BASE_URL + '/page/movies'}
    )
    yield Listitem.search(do_search)


@Route.register(content_type="videos")
def list_slider_page(_, url):
    """List the sliders found on pages like Home, Legend, and True Crime.

    Collections, a.k.a playlists, are shown in sliders on the page. The contents
    of these sliders are lazy loaded by the website and requested separately from
    /sliders/playlist/<PLAYLIST_ID> or /sliders/seriesPlaylist/<PLAYLIST_ID>.
    The whole collection is available at /playlist/<PLAYLIST_ID> or series/playlist/<PLAYLIST_ID>

    """
    root = fetch(url)
    main = root.find('*/main/page-sections')

    # List all collections
    for slider_div in main.iterfind("large-row/div"):
        slider_url = playlist_url(slider_div)
        title = clean_str(slider_div.find('.//h2').text)
        li = Listitem.from_dict(
            callback=list_grid_page,
            label=title,
            info={'plot': 'Collection'},
            params={'url': slider_url}
        )
        yield li


# This is currently not used, as all we request the whole playlist,
# like returned with the 'more' button.
@Route.register(content_type="videos")
def list_slider(_, url):
    """List the contents of a slider on a page, like the Home page."""
    root = fetch(url)
    yield from parse_slider(root)


def parse_slider(root):
    """Parse the contents of a slider.

    Used to parse slider content as seen on Home and other pages and search results.

    """
    slider_wrapper = root.find(".//div[@class='swiper-wrapper']")
    for slide in slider_wrapper.iterfind('div'):
        slide_contents = slide[0]
        if slide_contents.tag == 'div':
            yield parse_playlist_item(slide_contents)
        elif 'more-tile' in slide_contents.attrib['class']:
            yield parse_more_tile(slide_contents)


@Route.register(content_type="videos")
def list_grid_page(_, url):
    """A page that consists of a single grid of items.

    Used for pages Series and Movies and full playlist pages.
    """
    root = fetch(url)
    grid = root.find('*/main/page-sections/small-grid')
    if grid:
        path_spec = ".//div[@display-type='small_grid']"
    else:
        grid = root.find('*/main/page-sections/large-grid')
        path_spec = ".//div[@display-type='large_grid']"

    for video_item in grid.iterfind(path_spec):
        yield parse_playlist_item(video_item.find('div'))


@Route.register(redirect_single_item=True, content_type="videos")
def list_series(_, url):
    """List the seasons of a show.

    Redirects to series when only one season is available.
    """
    root = fetch(url)
    show_name = clean_str(root.find('.//h1').text)
    background = root.find(".//div[@class='component hero-background']")
    match = re.search(r"active: '([^']+)',", background.get('x-data', ''))
    show_img = match[1] if match else None
    seasons_list = root.find(".//ul[@aria-labelledby='season-selector']")
    for li in seasons_list.iterfind('li'):
        btn = li.find('button')
        title = clean_str(btn.text)
        target = btn.get('data-bs-target')

        item = Listitem()
        item.label = title
        item.set_callback(list_episodes, url=url, series=target.strip('#'))
        item.info['tvshowtitle'] = show_name
        item.art['thumb'] = show_img
        menu_utils.item_post_treatment(item, is_playable=False)
        yield item


@Route.register(content_type="episodes")
def list_episodes(_, url, series):
    """List the individual episodes of a show"""
    root = fetch(url)
    show_name = clean_str(root.find('.//h1').text)
    series_div = root.find(f".//div[@id='{series}']")
    for episode_div in series_div[0].iterfind("div"):
        # video_img = episode_div.find('.//img').get('src')
        data_span = episode_div.find(".//span[@data-uvid]")
        uvid = data_span.get('data-uvid')
        video_img = data_span.get('data-poster')
        video_title = data_span.get('data-title')
        season_episode = data_span.get('data-description', '')

        description = clean_str(episode_div.find(".//div[@x-data='{ open: false }']").text)

        play_btn_div = episode_div.find(".//template[@x-if='!$store.padlock.showPadlock']/div")
        play_btn_x_data = play_btn_div.get('x-data')
        match = re.search(r"warningMessage: '(.+?)',", play_btn_x_data, re.DOTALL)
        age_rating = match[1] if match else ''
        match = re.search(r"season: '(\d+)',", play_btn_x_data)
        if match:
            season_nr = int(match[1])
            match = re.search(r"episode: '(\d+)',", play_btn_x_data)
            episode_nr = int(match[1])
        else:
            season_nr = None
            episode_nr = None

        item = Listitem()
        item.label = '. ' .join((str(episode_nr), video_title))
        item.art['thumb'] = item.art['landscape'] = video_img
        item.info.update({
            'plot': ''.join((description, '\n\n', season_episode, '\n', age_rating)),
            'season': season_nr,
            'episode': episode_nr,
            'tvshowtitle': show_name,
            'duration': int(data_span.get('data-duration'), 0) or None
        })
        item.set_callback(play_vod, url=url, uvid=uvid)
        menu_utils.item_post_treatment(item, is_playable=True)
        yield item


@Route.register(content_type="videos")
def do_search(_, search_query):
    root = fetch(
        BASE_URL + '/search/results',
        params={'query': search_query,
                'showUvids': 'undefined',
                'uvid': 'undefined',
                'debugSkeleton': 'undefined',
                'debugSlider': 'undefined'}
    )
    # Note: Apparently, htmlelement adds a <html> root tag to the results.
    for slider in root.findall("div/slider"):
        bold_slider_title = ''.join(('[B]', clean_str(slider.find(".//h2").text), '[/B]', '\n'))
        for li in parse_slider(slider):
            if not li:
                continue
            # Search results are grouped into several sliders, like 'Movies',
            # or 'Series', etc. Add the slider's name to the description to
            # better indicate what kind of item it is.
            description = li.info['plot']
            li.info['plot'] = bold_slider_title + description
            yield li


@Resolver.register
def play_vod(plugin, uvid, **_):
    # Get tokens
    resp = urlquick.get(
        url='https://www.watchfreeuk.co.uk/api/player/token/' + uvid,
        headers={
            'user-agent': web_utils.get_random_ua(),
            'accept': 'application/json',
            'environment': 'production',
            'Referer': 'https://www.watchfreeuk.co.uk/'
        },
        timeout=REQ_TIMEOUT,
        max_age=0
    )
    try:
        tokens = json.loads(resp.content)
    except json.JSONDecodeError:
        check_geo_block(resp)
        raise
    analytics = json.loads(tokens['analytics'])

    # Get stream url
    headers = DFLT_HEADERS.copy()
    headers.update({
        'accept': 'application/json',
        'token': tokens['token'],
        'token-expiry': str(tokens['expiry']),
        'userid': '123456',
        'uvid': uvid
    })
    resp = urlquick.post(
        url='https://v2-streams-elb.simplestreamcdn.com/api/show/stream/' + uvid,
        headers=headers,
        params={'key': analytics['api_key'], 'platform': 'firefox'},
        timeout=REQ_TIMEOUT,
        max_age=-1
    )
    strm_data = json.loads(resp.content)
    strm_url = strm_data['response']['stream']
    return resolver_proxy.get_stream_with_quality(plugin, strm_url)
