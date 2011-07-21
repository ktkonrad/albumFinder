"""
basic youtube functionalities to search for a video
currently uses http api. need to switch to python api to make things cleaner
Kyle Konrad 7/20/2011
"""
#TODO: use python api to make this cleaner

import urllib, urllib2, re
from BeautifulSoup import BeautifulStoneSoup

api_url = 'https://gdata.youtube.com/feeds/api/videos'
key = 'AI39si6-uhxXoLQaPZsG0ilKLSr2ZPbdSSgektqhFl8sxNcOP86UgCEQfWEdDigd3efGIkBTOt9YE2QxJ4n4Q_AYXSl35WsTlw'
authsubsessiontoken_url = 'https://www.google.com/accounts/AuthSubSessionToken'
authsubrequest_url = 'https://www.google.com/accounts/AuthSubRequest'

def query(search_term):
    """search youtube
    returns query result as raw xml"""
    params = urllib.urlencode({'q' : search_term, 'key' : key})
    res = urllib2.urlopen("%s?%s" % (api_url, params)).read() # do it this way so it's a GET
    return res

def first_video(raw_xml):
    """get id of first video in search results"""
    xml = BeautifulStoneSoup(raw_xml)
    title_tag = xml.findAll('title')[1]
    link_tag = title_tag.findNextSibling('link')
    link = link_tag['href']
    match = re.search('\?v=([\w\-_]+)', link)
    video_id = match.group(1)
    return video_id

def get_video(search_term):
    """get first video from results for search_term"""
    return first_video(query(search_term))
    
