# -*- coding: utf-8 -*-
# @Time    : 2020/7/18 16:58
# @Author  : Xichagui
# @Site    :
# @File    : proxy_spider.py
# @Software: PyCharm
import datetime
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests
from lxml import html

from sqlalchemy import TIMESTAMP, Column, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import func
from util.util import Base, Session, init_db

FREE_PROXY_LIST = [
    'https://www.sslproxies.org',
    'https://free-proxy-list.net',
    'https://www.us-proxy.org',
    'https://free-proxy-list.net/uk-proxy.html',
    'https://free-proxy-list.net/anonymous-proxy.html',
]

XILADAILI = [
    'http://www.xiladaili.com/https/',
    'http://www.xiladaili.com/gaoni/',
]

HEADERS = {
    'Proxy-Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,zh-TW;q=0.6',
}

UA_LIST = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3764.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3764.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/82.0.3103.116 Safari/537.36',
    'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/11.0'
]

REQUEST_TIME_OUT = 5


class Proxy(Base):

    __tablename__ = 'proxy_ip'

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'schema': 'proxy'
    }

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    address = Column(String(50), nullable=False)
    http_type = Column(String(50), nullable=False)
    failure_times = Column(INTEGER(unsigned=True), default=0)
    create_time = Column(TIMESTAMP, default=datetime.datetime.now)
    update_time = Column(TIMESTAMP,
                         default=datetime.datetime.now,
                         onupdate=datetime.datetime.now)


class ProxyUtil():
    def __init__(self):
        self.proxy_list = []
        self.proxy_http_list = []
        self.proxy_https_list = []
        self.proxy_spider_lock = threading.Lock()
        self.condition = threading.Condition()
        # self.check_proxy_list()
        self.event = threading.Event()

    # 检测爬取的ip是否能用 检测地址为bagumi
    def check_ip_useful(self, proxy_ip, http_type='http'):
        temp_headers = HEADERS.copy()
        temp_headers['User-Agent'] = random.sample(UA_LIST, 1)[0]
        temp_headers['Host'] = 'bangumi.tv'
        temp_headers['Referer'] = f'{http_type}://bangumi.tv/anime'
        try:
            r = requests.get(
                f'{http_type}://bangumi.tv/anime/browser?sort=rank',
                headers=temp_headers,
                proxies={http_type: f'{http_type}://{proxy_ip}'},
                timeout=REQUEST_TIME_OUT)
            r.encoding = 'utf-8'

            # 通过匹配排名第一的星际牛仔 确定是否正确访问网页
            if re.search('星际牛仔', r.text):
                print(f'{http_type}://{proxy_ip} can be use. Great!!! ')
                self.proxy_list.append((proxy_ip, http_type))
            else:
                pass
                # print(f'{http_type}://{proxy_ip} got the wrong html. QAQ')
        except:
            pass
            # print(f'{http_type}://{proxy_ip} can not be ues. ')

    # 代理爬取
    def free_proxy_spider(self):
        proxy_list_uncheck = []
        proxy_list_uncheck.extend(self.free_proxy_list_spider())
        # proxy_list_uncheck.extend(self.xila_spider())

        self.check_ip_list(proxy_list_uncheck)

        session = Session()
        for proxy_ip, http_type in self.proxy_list:
            try:
                proxy = session.query(Proxy).filter(
                    Proxy.address == proxy_ip,
                    Proxy.http_type == http_type).one()
                proxy.failure_times = 0
            except NoResultFound:
                session.add(
                    Proxy(address=proxy_ip, http_type=http_type))
            except Exception as e:
                print(e)

            try:
                session.commit()
            except Exception as e:
                print(e)
                session.rollback()
        self.proxy_list = []
        session.close()


    # 发起代理请求
    def request_with_proxy(self,
                           url,
                           request_type='get',
                           headers=None,
                           timeout=REQUEST_TIME_OUT):

        http_type = urlparse(url).scheme
        if http_type not in ('https', 'http'):
            print('Need full url likes "http://xxx.com"')
            raise Exception('Need full url likes "http://xxx.com"')

        if request_type not in ['get', 'post']:
            print(f'The request_type "{request_type}" is not support.')
            raise Exception(
                f'The request_type "{request_type}" is not support.')

        request_func = getattr(requests, request_type)

        if not headers:
            headers = HEADERS.copy()
        else:
            headers = {**HEADERS.copy(), **headers}

        if 'User-Agent' not in headers:
            headers['User-Agent'] = random.sample(UA_LIST, 1)[0]

        proxies = self.get_proxy_ip(http_type)

        if not proxies:
            return False

        try:
            req = request_func(url,
                               headers=headers,
                               timeout=timeout,
                               proxies=proxies)
            return req
        except requests.exceptions.MissingSchema as e:
            # print(e)
            print('The url is wrong, please check the url.')
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ProxyError) as e:
            if http_type == 'http':
                proxy_ip = proxies['http']
                # self.proxy_http_list.remove(proxies['http'])
                print(proxies['http'] + '不可用.')
            else:
                # self.proxy_https_list.remove(proxies['https'])
                proxy_ip = proxies['https']
                print(proxies['https'] + '不可用.')
            session = Session()
            try:

                proxy = session.query(Proxy).filter(
                    Proxy.address == proxy_ip,
                    Proxy.http_type == http_type).first()
                proxy.failure_times += 1
                session.commit()
                return self.request_with_proxy(
                    url,
                    request_type='get',
                )
            except Exception as e:
                session.rollback()
                print('rollback')
                print(e)
                return False
            finally:
                session.close()

    # def check_proxy_list(self):
    #     try:
    #         if len(self.proxy_http_list) <= 5 or len(
    #                 self.proxy_https_list) <= 5:
    #
    #             if not self.proxy_spider_lock.acquire(blocking=False):
    #                 # print('wait')
    #                 self.event.wait()
    #                 # print('go')
    #             else:
    #                 # print('lock')
    #                 self.event.clear()
    #                 self.proxy_http_list = self.get_proxy_list('http')
    #                 self.proxy_https_list = self.get_proxy_list('https')
    #                 self.proxy_spider_lock.release()
    #                 self.event.set()
    #                 # print('release')
    #     except Exception as e:
    #         print(e)

    # def get_proxy_list(self, http_type):
    #     session = Session()
    #     try:
    #         print('重新加载代理ip')
    #         res = session.query(Proxy).filter(
    #             Proxy.http_type == http_type,
    #             Proxy.failure_times < 5).order_by(
    #                 func.random()).limit(20).all()
    #         proxy_list = [proxy.address for proxy in res]
    #
    #         if len(proxy_list) < 10:
    #             self.free_proxy_spider()
    #             proxy_list = self.get_proxy_list(http_type)
    #             return proxy_list
    #     except Exception as e:
    #         print(e)
    #         raise e
    #     finally:
    #         session.close()

    def get_proxy_ip(self, http_type):
        session = Session()
        try:
            proxies = {'http': None, 'https': None}
            # print('获取代理ip')
            res = session.query(Proxy).filter(
                Proxy.http_type == http_type,
                Proxy.failure_times < 5).order_by(
                    func.random()).limit(5).all()
            if len(res) == 5:
                self.event.set()
                proxies[http_type] = res[0].address
                print('get ip')
            else:
                self.event.clear()
                if self.proxy_spider_lock.acquire(blocking=False):
                    self.free_proxy_spider()
                    # print(threading.current_thread().name, 'set')
                    self.event.set()
                    self.proxy_spider_lock.release()
                else:
                    # print(threading.current_thread().name, 'wait')
                    self.event.wait()
                    # print(threading.current_thread().name, 'go')
                return self.get_proxy_ip(http_type)
            return proxies
        except Exception as e:
            print(11111111)
            print(e)
            return False
        finally:
            session.close()

    def check_ip_in_db(self):
        session = Session()
        executor = ThreadPoolExecutor(max_workers=10)
        exe_list = [executor.submit(self.check_ip_useful, p.address, p.http_type) for p in session.query(Proxy).all()]
        list(as_completed(exe_list))

    def free_proxy_list_spider(self):
        proxy_ips = []
        for url in FREE_PROXY_LIST:
            try:
                r = requests.get(url=url, timeout=REQUEST_TIME_OUT)
                if r.status_code == 200:
                    print(f'{url} done.')
                    html_text = r.text
                    ips = re.findall(
                        r"<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td><td>(\d{2,5})</td>.*?<td class=\'hx\'>(.*?)</td>",
                        html_text)
                    proxy_ips.extend([
                        (f'{ip}:{port}',
                         'https' if is_https_str == 'yes' else 'http')
                        for ip, port, is_https_str in ips
                    ])
            except Exception as e:
                print(f'error: {url} can not spider.')
                print(e)
        return proxy_ips

    def xila_spider(self):
        proxy_ips = []
        for url in XILADAILI:
            XILA_TYPE_DICT = {'HTTP代理': 0, 'HTTPS代理': 1, 'HTTP,HTTPS代理': 2}
            try:
                r = requests.get(url=url, timeout=REQUEST_TIME_OUT, headers=HEADERS)
                if r.status_code == 200:
                    print(f'{url} done.')
                    tree = html.fromstring(r.text)
                    x_res = tree.xpath('//tbody/tr/td/text()')

                    index = 0
                    while index < len(x_res):
                        xila_type = XILA_TYPE_DICT[x_res[index + 1]]
                        if xila_type == 0:
                            proxy_ips.append([x_res[index], 'http'])
                        elif xila_type == 1:
                            proxy_ips.append([x_res[index], 'https'])
                        elif xila_type == 2:
                            proxy_ips.append([x_res[index], 'http'])
                            proxy_ips.append([x_res[index], 'https'])
                        index += 8

            except Exception as e:
                print(f'error: {url} can not spider.')
                print(e)
        return proxy_ips

    def check_ip_list(self, ip_list):
        executor = ThreadPoolExecutor(max_workers=20)
        temp_l = [
            executor.submit(self.check_ip_useful, proxy_ip,
                            http_type)
            for proxy_ip, http_type in ip_list
        ]
        list(as_completed(temp_l))



if __name__ == '__main__':
    init_db()
    p = ProxyUtil()
    p.free_proxy_spider()
    # p.check_ip_in_db()

    # with open('xila.html', 'r') as f:
    #     tree = html.fromstring(f.read())
    #     tr = tree.xpath('//tbody/tr/td/text()')
        # print(tr)
        # for t in tr:
        #     print(t)
        # print(len(tr))
        # index = 0
        # while index < len(tr):
        #     print(tr[index], tr[index+1])
        #     index += 8