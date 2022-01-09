import re
import requests
import random
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
HEADER={
    'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36',
#     'Content-Type": "application/json'
#     'Referer': 'https://accounts.douban.com/passport/login_popup?login_source=anony',
#     'Origin': 'https://accounts.douban.com',
#     'content-Type':'application/x-www-form-urlencoded',
#     'x-requested-with':'XMLHttpRequest',
#     'accept':'application/json',
#     'accept-encoding':'gzip, deflate, br',
#     'accept-language':'zh-CN,zh;q=0.9',
#     'connection': 'keep-alive',
}