"""Basic functionalities to get album tracks from Amazon
Kyle Konrad 7/22/2011"""

import amazonproduct
from BeautifulSoup import BeautifulSoup
import urllib2, re

class Amazon():
    def __init__(self, aws_key, secret_key):
        self.api = amazonproduct.API(aws_key, secret_key, 'us')

    def get_tracks(self, album, artist):
        """get track titles from amazon
        returns a generator"""
        node = self.api.item_search('Music', Title=album, Artist=artist)
        album = node.Items.Item[0]
        detail_page_url = str(album.DetailPageURL)
        raw_html = urllib2.urlopen(detail_page_url).read()
        html = BeautifulSoup(raw_html)
        tracks_col = html.findAll(name='td', attrs={'class' : 'titleCol'})
        for table_entry in tracks_col:
            match = re.search('\d+\.(.+)', table_entry.text)
            if match:
                yield match.group(1)
