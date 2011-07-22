#!/usr/bin/env python2.6

"""
AlbumFinder v0.1

AlbumFinder is a bare-bones web app to create YouTube playlists for albums
Album info in fetched from Wikipedia

TODO: make track name parsing from wikipedia more robust.
      beter yet, get track names from amazon instead
"""

import urllib, urllib2
import wikipedia, youtube

import re
import web
import json
import urlparse

import gdata.youtube
import gdata.youtube.service

from BeautifulSoup import BeautifulStoneSoup

yt_service = gdata.youtube.service.YouTubeService()
yt_service.ssl = True
yt_service.client_id = 'AlbumFinder'

developer_key_filename = 'developer_key.txt'
developer_key_file = open(developer_key_filename)
yt_service.developer_key = developer_key_file.readline()[:-1] # drop trailing newline
developer_key_file.close()


api_playlist_base = 'http://gdata.youtube.com/feeds/api/playlists/'
playlist_base = 'http://youtube.com/playlist?list=PL'

urls = ['/playlist', 'Playlist']

app = web.application(urls, globals())

class Playlist():
    def GET(self):
        """get one-time token from youtube, exchange for session token"""
        params = urlparse.parse_qs(web.ctx.query[1:])
        if 'token' in params.keys(): # we have a one time token
            one_time_token = params['token'][0]
            yt_service.SetAuthSubToken(one_time_token)
            session_token = yt_service.UpgradeToSessionToken()
            artist = params['artist'][0]
            album = params['album'][0]
            title = "%s %s" % (artist, album)
            summary = "%s by %s. Playlist generated by AlbumFinder" % (album, artist)
            raw_xml = yt_service.AddPlaylist(title, summary)    
            match = re.search('<ns0:id>.*/([^/]+)</ns0:id>', str(raw_xml))
            if match:
                playlist_id = match.group(1)
                playlist_url = api_playlist_base + playlist_id
            else:
                raise Exception('could not parse playlist URL')
            for video_id in get_album_videos(artist, album):
                video_entry = yt_service.AddPlaylistVideoEntryToPlaylist(playlist_url, video_id)
            web.seeother(playlist_base + playlist_id)
        else: # get a one-time token
            params = urllib.urlencode({'next' : '%s%s' % (web.ctx.homedomain, web.ctx.fullpath), 'scope' : 'http://gdata.youtube.com', 'session' : '1', 'secure' : '0'})
            web.seeother("%s?%s" % (youtube.authsubrequest_url, params))

    POST = GET


def get_album_videos(artist, album):
    """helper function to get track names from wikipedia and corresponding videos from youtube"""
    tracks = wikipedia.get_tracks("%s %s album" % (artist, album))
    for track in tracks:
        video_id = youtube.get_video("%s %s" % (artist, track))
        if video_id:
            yield video_id


if __name__ == '__main__':
    app.run()

