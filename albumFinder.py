#!/usr/bin/env python

"""
AlbumFinder v0.2.3

AlbumFinder is a bare-bones web app to create YouTube playlists for albums
Album info in fetched from Wikipedia

TODO: make track name parsing from wikipedia more robust.
      beter yet, get track names from amazon instead
"""

version = '0.2.3'

# api imports
import amazonproduct
import gdata.youtube
import gdata.service

# local imports
import amazon as amzn
import youtube as yt
import logger

# python imports
import urllib, urlparse, re, web
from datetime import datetime
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('albumFinder.cfg')
youtube = yt.Youtube(config.get('youtube', 'developer_key'))

amazon = amzn.Amazon(config.get('amazon', 'aws_key'), config.get('amazon', 'secret_key'))

urls = ['/', 'Index',
        '/create_playlist', 'CreatePlaylist',
        '/show_playlist', 'ShowPlaylist',
        '/favicon.ico', 'Icon'
]

app = web.application(urls, globals())
render = web.template.render('templates/')

class CreatePlaylist():
    def GET(self):
        """get one-time token from youtube, exchange for session token"""
        params = urlparse.parse_qs(web.ctx.query[1:])
        if 'token' not in params.keys():
            return 'No youtube session token given'
        one_time_token = params['token'][0]
        youtube.upgrade_token(one_time_token)
        if 'artist' not in params.keys():
            return "please enter an artist"
        if 'album' not in params.keys():
            return "please enter an album"
        artist = params['artist'][0]
        album = params['album'][0]
        logger.log_request("%s, %s, %s, %s" % (datetime.now(), web.ctx.ip, artist, album))
        title = "%s %s" % (artist, album)
        summary = "%s by %s. Playlist generated by AlbumFinder" % (album, artist)
        try:
            album_videos = list(get_album_videos(artist, album))
        except amazonproduct.api.NoExactMatchesFound as e:
            logger.log_error("not found: %s, %s" % (artist, album))
            return 'Sorry, that album could not be found.'

        try:
            playlist_id = youtube.add_playlist(title, summary)
            for video_id in album_videos_generator:
                youtube.add_video_to_playlist(video_id, playlist_id)
            web.seeother("/show_playlist?playlist_id=%s" % playlist_id)
        except gdata.service.RequestError as e:
            if re.search('Playlist already exists', str(e)):
                logger.log_error("already exists: %s" % title)
                return 'Sorry, that playlist already exists.'
            else:
                logger.log_error(str(e))
                raise e
    POST = GET

class ShowPlaylist:
    def GET(self):
        params = urlparse.parse_qs(web.ctx.query[1:])
        if 'playlist_id' not in params.keys():
            return 'No playlist id given'
        playlist_id = params['playlist_id'][0]

        return render.playlist(playlist_id)


album_artist_form = web.form.Form(
    web.form.Textbox('artist', web.form.notnull),
    web.form.Textbox('album', web.form.notnull)
)
        
class Index():
    def GET(self):
        form = album_artist_form()
        return render.index(form)

    def POST(self):
        form = album_artist_form()
        if not form.validates():
            return render.index(form)
        else:
            playlist_params = urllib.urlencode({'album' : form.album.value, 'artist' : form.artist.value})
            authsub_url = youtube.get_authsub_url('%s/create_playlist?%s' % (web.ctx.homedomain, playlist_params))
            web.seeother(authsub_url)

class Icon():
    def GET(self):
        web.header('Content-Type', 'image/x-icon')
        return open('favicon.ico', 'rb').read()

def get_album_videos(artist, album):
    """helper function to get track names from amazon and corresponding videos from youtube"""
    tracks = amazon.get_tracks(album, artist)
    for track in tracks:
        video_id = youtube.query("%s %s" % (artist, track))
        if video_id:
            yield video_id


if __name__ == '__main__':
    app.run()

