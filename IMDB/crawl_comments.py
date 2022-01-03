import re
import requests
import random
from bs4 import BeautifulSoup, StopParsing
import pandas as pd
import time
import urllib
HEADER={
    'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36',
#     'Referer': 'https://accounts.douban.com/passport/login_popup?login_source=anony',
#     'Origin': 'https://accounts.douban.com',
#     'content-Type':'application/x-www-form-urlencoded',
#     'x-requested-with':'XMLHttpRequest',
#     'accept':'application/json',
#     'accept-encoding':'gzip, deflate, br',
#     'accept-language':'zh-CN,zh;q=0.9',
#     'connection': 'keep-alive',
 }

class CrawlComments:

    def __init__(self, start_url, url_temp, dump2csv=False, dump_file_name=None):
        self.start_url = start_url
        self.url_temp = url_temp
        self.dump2csv = dump2csv
        self.dump_file_name = dump_file_name
        self.res = {
            "contents": [],
            "rates": [],
            "times": []
        }
        self.next_key = None

    def _crawl_html(self, url):
        res = requests.get(url, headers=HEADER)
        return res

    def _parse_html(self, string):
        return BeautifulSoup(string, "lxml")
    
    def get_comment_info(self, soup):
        items = soup.select('.lister-item.mode-detail.imdb-user-review')
        times, rates, contents = [], [], []

        for item in items:
            try:
                time = item.select('.review-date')[0].text.strip()
                time = time.replace('\n', ' ')
            except Exception as e:
                print("time", e)
                time = "1970:01:01 00:00:00"
            
            try:
                content = item.select('.text.show-more__control')[0].text.strip()
                content = content.replace('\n', ' ')
            except Exception as e:
                print("content", e)
                content = ""
            
            try:
                rate = item.select('.rating-other-user-rating')[0].text.strip()
                rate = rate.replace('\n', '')[:-3]
            except Exception as e:
                rate = ""
                print("rate", e)
            
            if content == "" and rate == "":
                continue

            times.append(time)
            rates.append(rate)
            contents.append(content)
            
        return times, rates, contents

    def craw_single_page(self, url):
        response = self._crawl_html(url)
        s_code = response.status_code
        if s_code != 200:
            print("status_code: %d, url %s is in trouble, skip this" % (s_code, url))
            return -3
        
        soup = self._parse_html(response.text)
        self.soup = soup
        times, rates, contents = self.get_comment_info(soup)

        if len(times) == 0 and len(rates) == 0 and len(contents) == 0:
            print("status code: %d, no more data" % (-2))
            return -2

        if len(times) != len(rates) or len(times) != len(contents):
            print("status code: %d, times: %d, rates: %d, contents: %d, not equal, \n the url is %s" % (-1, len(times), len(rates), len(contents), url))
            return -1

        self.res["times"] += times
        self.res["rates"] += rates
        self.res["contents"] += contents
        try:
            self.next_key = soup.select('.load-more-data')[0].attrs['data-key'].strip()
        except Exception as e:
            self.next_key = None
            print('find key exception %s', e)
        return 0

    def start_crawl(self):
        print("======Start Crawling, plz wait======")

        self.craw_single_page(self.start_url)
        
        while self.next_key != None:
            try:
                if len(self.res['rates']) % 100 == 0:
                    print("I have crawled %d comments. Your movie is so popular" % len(self.res['rates']))
                time.sleep(random.randint(10, 20))
                url = self.url_temp % self.next_key
                status_code = self.craw_single_page(url)
                if status_code == -2:
                    break
            except KeyboardInterrupt:
                break

        if len(self.res['times']) == 0 and len(self.res['rates']) == 0 and len(self.res['contents']):
            print('WARNING: There is no data for url, plz check your url\n')
            return

        df = pd.DataFrame.from_dict(self.res)
        df = df[['times', 'rates', 'contents']]
        if self.dump2csv:
            dump_file_name = self.dump_file_name
            if dump_file_name is None:
                cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                dump_file_name = cur_time + '.csv'
            df.to_csv(dump_file_name, index=None)
        print("======Thx for your patience, I crawled %d data=====" % (df.shape[0]))

if __name__ == "__main__":
    # start_url = 'https://www.imdb.com/title/tt0112471/reviews?ref_=tt_urv'
    # next_url_tmpl = 'https://www.imdb.com/title/tt0112471/reviews/_ajax?ref_=undefined&paginationKey=%s'
    start_url = "https://www.imdb.com/title/tt2209418/reviews?ref_=tt_urv"
    next_url_tmpl = 'https://www.imdb.com/title/tt2209418/reviews/_ajax?ref_=undefined&paginationKey=%s'
    
    craw_spider = CrawlComments(start_url, next_url_tmpl, True, "./before_midnight.csv")
    craw_spider.start_crawl()

