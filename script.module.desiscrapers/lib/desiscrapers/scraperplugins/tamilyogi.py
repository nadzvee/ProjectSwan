import re
import urllib
import urlparse
import json


from BeautifulSoup import BeautifulSoup, SoupStrainer
from aftershock.common import cleantitle, client, logger, jsunpack
from ..scraper import Scraper


class TamilYogi(Scraper):
    domains = ['tamilyogi.fm', 'tamilyogi.cc']
    name = "tamilyogi"

    def __init__(self):
        self.base_link = 'http://www.tamilyogi.fm'
        self.search_link = '/feed/?search=Search&s=%s'
        self.srcs = []

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:
            query = title
            query = self.search_link % (urllib.quote_plus(query))
            query = urlparse.urljoin(self.base_link,query)

            result = client.request(query, error=True)

            items = client.parseDOM(result, "item")

            cleanedTitle = cleantitle.get(title)
            for item in items:
                linkTitle = client.parseDOM(item, "title")[0]

                if cleanedTitle in cleantitle.get(linkTitle):
                    url = client.parseDOM(item, "link")[0]
                    break

            return self.sources(client.replaceHTMLCodes(url))
        except Exception as e:
            logger.error('[%s] Exception : %s' % (self.__class__, e))
            pass
        return []

    def sources(self, url):
        logger.debug('SOURCES URL %s' % url, __name__)
        try:
            srcs = []

            if url == None: return srcs

            if 'hd' in url.lower():
                quality = 'HD'
            else:
                quality = 'SD'

            html = client.request(url)

            mlink = SoupStrainer("div", {"class":"entry"})
            videoclass = BeautifulSoup(html, parseOnlyThese=mlink)

            try:
                links = videoclass.findAll('iframe')

                for link in links:
                    url = link.get('src')
                    host = client.host(url)
                    srcs.append({'source': host, 'parts': '1', 'quality': quality, 'scraper':self.name, 'url': url, 'direct':False})

            except:
                pass

            return srcs
        except:
            return srcs