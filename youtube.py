"""
basic youtube functionalities to search for a video and add it to a playlist
Kyle Konrad 7/20/2011
"""
#TODO: use python api to make this cleaner

import urllib, urllib2, re
from BeautifulSoup import BeautifulStoneSoup


import gdata.youtube
import gdata.youtube.service

yt_service = gdata.youtube.service.YouTubeService()
yt_service.ssl = True
yt_service.client_id = 'AlbumFinder'

developer_key_filename = 'developer_key.txt'
developer_key_file = open(developer_key_filename)
yt_service.developer_key = developer_key_file.readline()[:-1] # drop trailing newline
developer_key_file.close()

api_playlist_base = 'http://gdata.youtube.com/feeds/api/playlists/'
playlist_base = 'http://youtube.com/playlist?list=PL'
api_url = 'https://gdata.youtube.com/feeds/api/videos'
authsubsessiontoken_url = 'https://www.google.com/accounts/AuthSubSessionToken'
authsubrequest_url = 'https://www.google.com/accounts/AuthSubRequest'

def query(search_term):
    """search youtube
    returns id of first result"""
    query = gdata.youtube.service.YouTubeVideoQuery()
    query.vq = search_term
    feed = yt_service.YouTubeQuery(query)
    return feed.entry[0].id.text
    
def add_playlist(title, summary):
    """create a playlist and return its ID"""
    raw_xml = yt_service.AddPlaylist(title, summary)
    match = re.search('<ns0:id>.*/([^/]+)</ns0:id>', str(raw_xml))
    if match:
        return match.group(1)
    else:
        raise Exception('could not parse playlist URL')

def upgrade_token(one_time_token):
    """upgrade a one-time token to a session token"""
    yt_service.SetAuthSubToken(one_time_token)
    try:
        session_token = yt_service.UpgradeToSessionToken()
    except Exception as e:
        return 'failed to created session token: %s' % str(e)

def add_video_to_playlist(video_id, playlist_id):
    playlist_url = api_playlist_base + playlist_id
    video_entry = yt_service.AddPlaylistVideoEntryToPlaylist(playlist_url, video_id)
    #TODO: check success
