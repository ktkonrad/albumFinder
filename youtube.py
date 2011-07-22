"""
basic youtube functionalities to search for a video and add it to a playlist
Kyle Konrad 7/20/2011
"""

import urllib, urllib2, re
from BeautifulSoup import BeautifulStoneSoup

import gdata.youtube
import gdata.youtube.service

class Youtube():
    api_playlist_base = 'http://gdata.youtube.com/feeds/api/playlists/'
    playlist_base = 'http://youtube.com/playlist?list=PL'
    authsubrequest_url = 'https://www.google.com/accounts/AuthSubRequest'
    
    def __init__(self, developer_key):
        self.yt_service = gdata.youtube.service.YouTubeService()
        self.yt_service.ssl = True
        self.yt_service.client_id = 'AlbumFinder'
        self.yt_service.developer_key = developer_key
    
    
    def query(self, search_term):
        """search youtube
        returns id of first result"""
        query = gdata.youtube.service.YouTubeVideoQuery()
        query.vq = search_term
        feed = self.yt_service.YouTubeQuery(query)
        return feed.entry[0].id.text
        
    def add_playlist(self, title, summary):
        """create a playlist and return its ID"""
        raw_xml = self.yt_service.AddPlaylist(title, summary)
        match = re.search('<ns0:id>.*/([^/]+)</ns0:id>', str(raw_xml))
        if match:
            return match.group(1)
        else:
            raise Exception('could not parse playlist URL')
    
    def upgrade_token(self, one_time_token):
        """upgrade a one-time token to a session token"""
        self.yt_service.SetAuthSubToken(one_time_token)
        try:
            session_token = self.yt_service.UpgradeToSessionToken()
        except Exception as e:
            return 'failed to created session token: %s' % str(e)
    
    def add_video_to_playlist(self, video_id, playlist_id):
        playlist_url = Youtube.api_playlist_base + playlist_id
        video_entry = self.yt_service.AddPlaylistVideoEntryToPlaylist(playlist_url, video_id)
        #TODO: check success
