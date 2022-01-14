from os import execlp, execlpe, name
from bs4 import BeautifulSoup
from bs4.builder import TreeBuilder
from bs4.element import SoupStrainer
import requests
import conf    
import datetime
import re
import random
import time
from utils import send_mail

class MovieInfo():
    def __init__(self, type_list, date, duration, rate, country, name, m_id, link):
        self.type_list = type_list
        self.date = date
        self.duration = duration
        self.country = country
        self.rate = rate
        self.name = name
        self.m_id = m_id
        self.link = link
    
    def __str__(self):
        return "{}-{}-{}-{}-{}-{}-{}-{}".format(self.m_id,
                                                self.name,
                                                self.date,
                                                self.rate,
                                                self.duration,
                                                self.country,
                                                '/'.join(self.type_list),
                                                self.link)

class RecBySelf():
    
    def __init__(self, cookie_path, account_id, topk=10, rate_thres=8.0, duration_thres=0.0, content_type=None, country=None, debug=False, send_email=False):
        self.cookie_path = cookie_path
        self.topk = topk
        self.account_id = account_id
        self.rate_thres = rate_thres
        self.duration_thres = duration_thres
        self.content_type = content_type.strip() if content_type is not None else None
        self.country = country.strip() if country is not None else None
        self.debug = debug
        self.send_email = send_email
        self.url_prefix = 'https://movie.douban.com/'
        self.url_suffix = '/wish?start=0&sort=time&rating=all&filter=all&mode=grid'
        self.cur_url = self.url_prefix + 'people/' + str(self.account_id) + self.url_suffix
        self.movie_infos = {}
        self.type2movies = {}
        self.rate2movies = {}
        self.country2movies = {}
        self.duration2movies = {}
        self.date2movies = {}
        self._load_cookies()

    def _load_cookies(self):
        cookies = open(self.cookie_path).readlines()[0]
        self.cookies = {
            'cookies': cookies
        }

    def add2type(self, type_list, m_id):
        for t in type_list:
            if t not in self.type2movies:
                self.type2movies[t] = []
            self.type2movies[t].append(m_id)

    def add2rate(self, rate, m_id):
        if rate not in self.rate2movies:
            self.rate2movies[rate] = []
        self.rate2movies[rate].append(m_id)
    
    def add2country(self, country, m_id):
        if country not in self.country2movies:
            self.country2movies[country] = []
        self.country2movies[country].append(m_id)
    
    def add2duration(self, duration, m_id):
        if duration not in self.duration2movies:
            self.duration2movies[duration] = []
        self.duration2movies[duration].append(m_id)

    def _get_url_soup(self, url):
        time.sleep(random.randint(2, 5))
        rsp = requests.get(url, headers=conf.HEADER, cookies=self.cookies)
        soup = BeautifulSoup(rsp.text, 'lxml')
        return soup

    def _get_movie_info(self, movie_link):
        soup = self._get_url_soup(movie_link)

        def _min_date(release_dates):
            
            def _change2datetime(date_string):
                date_string = re.search('(\d+-\d+-\d+).*', date_string).group(1)
                date_string = [int(i) for i in date_string.strip().split('-')]
                return datetime.datetime(*date_string)
            
            first_r_date = _change2datetime(release_dates[0].text)
            for temp_r in release_dates[1:]:
                temp_r_date = _change2datetime(temp_r.text)
                if first_r_date > temp_r_date:
                    first_r_date = temp_r_date
            return str(first_r_date.date())
        
        type_list = []
        for t in soup.select('span[property*=v\:genre]'):
            type_list.append(t.text.strip())
        
        exceptions = []
        try:
            date = _min_date(soup.select('span[property*=v\:initialReleaseDate]'))
        except Exception as e:
            exceptions.append(('date', e))

        try:
            duration = soup.select_one('span[property*=v\:runtime]').text.strip()
            duration = re.search('(\d+)', duration).group(1)
        except Exception as e:
            exceptions.append(('duration', e))
        
        try:
            rate = soup.select_one('strong[property*=v\:average]').text.strip()
        except Exception as e:
            exceptions.append(('rate', e))
        
        try:
            country = re.search('<span class="pl">制片国家/地区:</span>(.*?)<br/>', str(soup)).group(1)
        except Exception as e:
            exceptions.append(('country', e))
        
        try:
            name = soup.select_one('span[property*=v\:itemreviewed]').text.strip()
        except Exception as e:
            exceptions.append('name', e)

        if len(exceptions) > 0:
            print(exceptions, movie_link)
            return []
        return [type_list, date, float(duration), float(rate), country.strip(), name.strip()]
    
    def get_movies_link(self, url):

        soup = self._get_url_soup(url)
        items = soup.select('.item')
        for item in items:
            try:
                movie_link = item.select_one('.title > a').attrs['href']
            except Exception as e:
                print('no movie link')
                continue
            
            movie_info = self._get_movie_info(movie_link)
            if len(movie_info) == 0:
                continue
            m_types, m_r_date, m_duration, m_rate, m_country, _ = movie_info
            m_id = re.search('/(\d+)/', movie_link).group(1)

            if self.country != None and m_country != self.country:
                print('filter by country', movie_link, m_country)
                continue
            
            if self.rate_thres > float(m_rate):
                print('filter by rate', movie_link, m_rate)
                continue
            
            if self.duration_thres < float(m_duration):
                print('filter by duration', movie_link, m_duration)
                continue
            
            if self.content_type != None and self.content_type not in m_types:
                print('filter by type', movie_link, m_types)
                continue
            
            if m_id not in self.movie_infos:
                movie_info.append(m_id)
                movie_info.append(movie_link)
                self.movie_infos[m_id] = MovieInfo(*movie_info)
                # print(str(self.movie_infos[m_id]))
                
            self.add2country(m_country, m_id)
            self.add2duration(m_duration, m_id)
            self.add2rate(m_rate, m_id)
            self.add2type(m_types, m_id)
            
        next_url = soup.select_one('.next > a')
        if next_url is None:
            return None
        else:
            return next_url.attrs['href']

    def _start_crawl(self):
        cur_url = self.cur_url
        index = 1
        while True:
            cur_url = self.get_movies_link(cur_url)
            if cur_url == None or cur_url == '':
                break
            cur_url = self.url_prefix + cur_url
            if self.debug and index > 1:
                break
            if len(self.movie_infos) % 20 == 0:
                print('Thx for ur patience, I have collected %d films which you like, I will recommend some to you later' % len(self.movie_infos))
            index += 1
        
    def recommend(self):
        self._start_crawl()
        keys = self.movie_infos.keys()
        selected_keys = random.sample(keys, self.topk)
        print('I found that you have collect %d movies' % len(self.movie_infos))
        print('I recommend top %d for you to watch' % self.topk)
        # name rate type duration country
        content_format ="<p>%s, %f, %smin, %s, %s   <a href=%s>Douban Link</a></p>"
        content = "<p>Happy Weekend~</p><p>Enjoy your movie time~</p><p>Recommend %d movies for you</p>" % self.topk
        content += "<p>Name, Rate, Duration, Types, Country, Douban Link</p>"
        for k in selected_keys:
            m_info = self.movie_infos[k]
            content += content_format % (m_info.name, m_info.rate, m_info.duration, "/".join(m_info.type_list), m_info.country, m_info.link)
            # print(self.movie_infos[k].name, self.movie_infos[k].link)
        if self.send_email:
            send_mail(conf.EMAIL_ACCOUNT, conf.EMAIL_PASSWORD, conf.DST_EMAIL, conf.MAIL_HOST, content)
        else:
            print(content)

if __name__ == "__main__":
    rec_obj = RecBySelf('cookies', 175455903, 4, debug=True)
    rec_obj._get_movie_info('https://movie.douban.com/subject/35360296/')