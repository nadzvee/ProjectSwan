# -*- coding: utf-8 -*-

'''
    Genesis Add-on
    Copyright (C) 2015 lambda

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import re,urllib,urlparse,datetime, random

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib import resolvers
from resources.lib.libraries import metacache

class source:
    def __init__(self):
        self.base_link = 'http://www.apnaview.com'
        self.search_link = '/browse/?q=%s'
        self.now = datetime.datetime.now()
        self.theaters_link = '/browse/hindi/?year=%s' % (self.now.year)
        self.added_link = '/browse/hindi/?'
        self.sort_link = '&order=desc&sort=date'

    def scn_full_list(self, url):
        tmpList = []
        self.list = []

        pagesScanned = 0
        try : url = getattr(self, url + '_link')
        except:pass

        links = [self.base_link, self.base_link, self.base_link]
        for base_link in links:
            try: result = client.source(base_link + url + self.sort_link)
            except:
                result = ''

            if 'row movie-list' in result: break

        result = result.decode('iso-8859-1').encode('utf-8')
        movies = client.parseDOM(result, "div", attrs={"class":"movie"})

        for movie in movies:
            try :
                title = client.parseDOM(movie, "span", attrs={"class":"title"})[0]
                title = client.replaceHTMLCodes(title)
                try : title = title.encode('utf-8')
                except: pass

                year = client.parseDOM(movie, "small")[0]
                year = re.compile('(.+?) watch online').findall(year)[0]
                year = year.encode('utf-8')

                name = '%s (%s)' % (title, year)
                try: name = name.encode('utf-8')
                except: pass

                url = client.parseDOM(movie, "a", ret="href")[0]
                url = client.replaceHTMLCodes(url)
                try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
                except: pass

                poster = '0'
                try: poster = client.parseDOM(movie, "img", ret="src")[0]
                except: pass
                poster = client.replaceHTMLCodes(poster)
                try: poster = urlparse.parse_qs(urlparse.urlparse(poster).query)['u'][0]
                except: pass
                poster = poster.encode('utf-8')

                genre = '0' ; duration = 0 ; rating = 0; votes = 0; director = ''; cast = '' ; plot = ''; tagline = ''; mpaa = ''; next = ''; tvdb = '0'

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': '0', 'studio': '0', 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': '0', 'cast': cast, 'plot': plot, 'tagline': tagline, 'name': name, 'tvdb': tvdb, 'tvrage': '0', 'poster': poster, 'banner': '0', 'fanart': '0', 'lang':'en','next': next})
            except:
                pass
        try :
            next = client.parseDOM(result, "li", attrs={"class":"next page"})
            url = client.parseDOM(next, "a", ret="href")[0]
            url = re.compile('(.+?)&amp;page=(.+?)').findall(url)[0]
            self.list[0].update({'next':url[0]+'&page='+url[1]})
        except:
            client.printException('Exception in NEXT')
            pass

        self.list = metacache.fetchImdb(self.list)
        return self.list

    def get_movie(self, imdb, title, year):
        try:
            self.base_link = self.base_link
            query = '%s' % (title)
            query = self.search_link % (urllib.quote_plus(query))
            query = urlparse.urljoin(self.base_link, query)

            result = client.source(query)

            result = result.decode('iso-8859-1').encode('utf-8')
            result = client.parseDOM(result, "div", attrs={"class":"movie"})

            title = cleantitle.movie(title)
            for item in result:
                searchTitle = client.parseDOM(item, "span", attrs={"class":"title"})[0]
                searchTitle = cleantitle.movie(searchTitle)
                if title == searchTitle:
                    url = client.parseDOM(item, "a", ret="href")[0]
                    break
            if url == None or url == '':
                raise Exception()
            return url
        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            quality = 'CAM'
            sources = []

            if url == None: return sources

            url = '%s%s' % (self.base_link, url)

            try: result = client.source(url)
            except: result = ''

            result = result.decode('iso-8859-1').encode('utf-8')

            #result = result.replace('\n','')
            result = client.parseDOM(result, "table", attrs={"class":"table table-bordered"})[0]
            result = client.parseDOM(result, "tbody")[0]
            result = client.parseDOM(result, "tr")

            for item in result:
                try :
                    host = client.parseDOM(item, "td")[0].lower()
                    urls = client.parseDOM(item, "td")[1]
                    urls = client.parseDOM(urls, "a", ret="href")
                    for i in range(0, len(urls)):
                        videoID = re.compile('/video/(.+?)/').findall(urls[i] + '/')[0]
                        urls[i] = 'http://www.awesomevids.pw/video/%s' % videoID
                    if len(urls) > 1:
                        url = "##".join(urls)
                    else:
                        url = urls[0]
                    sources.append({'source': host, 'parts' : str(len(urls)), 'quality': quality, 'provider': 'ApnaView', 'url': url})
                except :
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            tUrl = url.split('##')
            if len(tUrl) > 0:
                url = tUrl
            else :
                url = urlparse.urlparse(url).path

            links = []
            for item in url:
                result = client.source(item, mobile=False)
                if 'Could not connect to mysql! Please check your database' in result:
                    result = client.source(item, mobile=True)

                try :
                    item = client.parseDOM(result, "div", attrs={"class":"videoplayer"})[0]
                    item = re.compile('(SRC|src|data-config)=\"(.+?)\"').findall(item)[0][1]
                except :
                    pass
                links.append(resolvers.request(item))
            url = links
            return url
        except:
            return