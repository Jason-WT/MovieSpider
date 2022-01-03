import re
import requests
import random
from bs4 import BeautifulSoup
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

# find your cookies in the douban website
COOKIES = {
    'cookie': 
}

class CrawlComments:

    def __init__(self, url_temp, login_name, login_password, dump2csv=False, dump_file_name=None):
        self.url_temp = url_temp
        self.login_name = login_name
        self.login_password = login_password
        self.dump2csv = dump2csv
        self.dump_file_name = dump_file_name
        self.res = {
            "contents": [],
            "rates": [],
            "times": []
        }
        self.cookies = None
        self.login_url = 'https://accounts.douban.com/j/mobile/login/basic'
        self._get_cookies()


    def _get_cookies(self):
        data = {
            'ck':'',
            'name': self.login_name,
            'password': self.login_password,
            'remember':'false',
            'ticket':''
        }
        data = urllib.parse.urlencode(data)
        req = requests.post(url, headers=HEADER, data=data, verify=False)
        cookies = requests.utils.dict_from_cookiejar(req.cookies)
        self.cookies = cookies
        self.cookies = COOKIES
        print(cookies)

    def _crawl_html(self, url):
        res = requests.get(url, headers=HEADER, cookies=self.cookies)
        return res

    def _parse_html(self, string):
        return BeautifulSoup(string, "lxml")

    def _get_all_time(self, soup):
        res = soup.find_all("span", attrs={"class": "comment-time"})
        res = list(map(lambda x: x.text.strip(), res))
        return res

    def _get_all_content(self, soup):
        res = soup.find_all(attrs={"class": "comment-content"})
        res = list(map(lambda x: x.text.strip(), res))
        return res

    def _get_all_rates(self, soup):
        res = soup.find_all(class_=re.compile("allstar.*rating"))
        res = list(map(lambda x: x.attrs["class"][0].strip()[-2], res))
        return res
    
    def get_comment_info(self, soup):
        items = soup.select('.comment-item')
        times, rates, contents = [], [], []

        for item in items:
            try:
                time = item.select(".comment-time")[0].text.strip()
                time = time.replace('\n', ' ')
            except Exception as e:
                print("time", e)
                time = "1970:01:01 00:00:00"
            
            try:
                content = item.select(".short")[0].text.strip()
                content = content.replace('\n', ' ')
            except Exception as e:
                print("content", e)
                content = ""
            
            try:
                rate = item.select(".comment-info")[0].select('span')[1].attrs['class'][0][-2]
                rate = rate.replace('\n', '')
            except Exception as e:
                rate = ""
                print("rate", e)
            
            if content == "" and rate == "":
                continue

            times.append(time)
            rates.append(rate)
            contents.append(content)
            
        return times, rates, contents

    def craw_time_rate_context(self, soup):
        times = self._get_all_time(soup)
        rates = self._get_all_rates(soup)
        contents = self._get_all_content(soup)
        
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
        return 0

    def start_crawl(self):
        print("======Start Crawling, plz wait======")

        start = 0
        while True:
            try:
                if start % 100 == 0:
                    print("I have crawled %d comments. Your movie is so popular" % start)
                time.sleep(random.randint(10, 20))
                url = self.url_temp % start
                status_code = self.craw_single_page(url)
                if status_code == -2:
                    break
                start += 20
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
    url = "https://movie.douban.com/subject/30346880/comments?start=%d&limit=20&status=P&sort=new_score"
    craw_spider = CrawlComments(url, 'your_account', 'your_password', True, "data/the_bankers_douban.csv")
    craw_spider.start_crawl()

