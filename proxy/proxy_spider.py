# -*- coding: utf-8 -*-
# @Time    : 2020/7/18 16:58
# @Author  : Xichagui
# @Site    :
# @File    : proxy_spider.py
# @Software: PyCharm
import random
import re

import requests
from requests import ConnectTimeout

from util.util import Db

urls = [
    "https://www.sslproxies.org",
    # "https://free-proxy-list.net",
    # "https://www.us-proxy.org",
    # "https://free-proxy-list.net/uk-proxy.html",
    # "https://free-proxy-list.net/anonymous-proxy.html",
]

headers = {
    'Host': 'bangumi.tv',
    'Proxy-Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer': 'http://bangumi.tv/anime',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,zh-TW;q=0.6',
}

# 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
ua = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3764.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3764.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/82.0.3103.116 Safari/537.36',
    'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/11.0'
]


def check_ip_useful(proxy_ip, http_type='http'):
    temp_headers = headers.copy()
    temp_headers['User-Agent'] = random.sample(ua, 1)[0]
    try:
        r = requests.get(f'{http_type}://bangumi.tv/anime/browser?sort=rank',
                         headers=temp_headers,
                         proxies={http_type: f'{http_type}://{proxy_ip}'},
                         timeout=5)
        r.encoding = 'utf-8'
        if re.search('白石稔', r.text):
            print(f'{proxy_ip} can be use. Great!!! ')
        else:
            print(f'{proxy_ip} got the wrong html. QAQ')
    except:
        print(f'{proxy_ip} can not be ues. ')


def free_proxy_spider():
    for url in urls:
        proxy_ips = []
        try:
            r = requests.get(url=url)
            if r.status_code == 200:
                print(f'{url} done.')
                html_text = r.text
                ips = re.findall(
                    r"<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td><td>(\d{2,5})</td>.*?<td class=\'hx\'>(.*?)</td>",
                    html_text)
                proxy_ips.extend([(f'{ip}:{port}',
                                   'https' if is_https_str == 'yes' else 'http')
                                  for ip, port, is_https_str in ips])
                # testing 5
                for proxy_ip, http_type in proxy_ips[:5]:
                    check_ip_useful(proxy_ip, http_type)
        except:
            print(f'error: {url} can not spider.')



if __name__ == '__main__':
    # temp_headers = headers.copy()
    # temp_headers['User-Agent'] = random.sample(ua, 1)
    # # requests.get('http://bangumi.tv/anime/browser?sort=rank', headers=temp_headers)
    # print(temp_headers == headers)
    # free_proxy_spider()
    db = Db('proxy')
    db.table_name = 'proxy_ip'
    print(db.select_db(sql = 'select * from proxy_ip'))