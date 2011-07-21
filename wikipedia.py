"""
basic wikipedia functionalities to get track names for an album
Kyle Konrad 7/20/2011
"""

import urllib, urllib2, re
from BeautifulSoup import BeautifulSoup

wiki_url = 'http://en.wikipedia.org/wiki'
api_url = 'http://en.wikipedia.org/w/api.php'

def query(search_term):
    """search wikipedia
    returns query result as raw xml"""
    params = urllib.urlencode({'action' : 'query', 'list': 'search', 'format' : 'xml', 'srsearch' : search_term})
    res = urllib2.urlopen(api_url, params)
    return res.read()

def first_title(xml):
    """get the title of the first page in a query result
    return None if there are no results
    uses regexp match, does not parse xml"""
    m = re.search('title="([^"]+)"', xml)
    try:
        return m.group(1)
    except:
        return None

def get_page(title):
    """get page by title
    returns page as raw html"""
    encoded_title = re.sub(' ', '_', title) # TODO: this should probably be more sophisticated...
    #print "opening %s/%s" % (wiki_url, encoded_title)
    request = urllib2.Request("%s/%s" % (wiki_url, encoded_title), headers={'User-agent' : 'AlbumFinder/0.1'})
    return urllib2.urlopen(request).read()

def parse_tracks(raw_html):
    """get track names from a wikipedia page
    input page as raw html
    output track names as list of strings"""
    html = BeautifulSoup(raw_html)
    # TODO: handle parsing failure
    tracks_tables = html.findAll(name='table', attrs={'class': 'tracklist'})
    for tracks_table in tracks_tables:
        for row in tracks_table('tr'):
            if row.td and row.td.findNextSibling('td'):
                raw_track_name = row.td.findNextSibling('td').text
                match = re.match('"(.*)"', raw_track_name)
                track_name = match.group(1)
                yield track_name

def get_tracks(search_term):
    """return generator for track names for album found by search_term"""
    result = query(search_term)
    title = first_title(result)
    page = get_page(title)
    tracks = parse_tracks(page)
    return tracks
