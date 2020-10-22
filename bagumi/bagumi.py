# -*- coding: utf-8 -*-
# @Time    : 2020/7/29 16:43
# @Author  : Xichagui
# @Site    :
# @File    : bagumi.py
# @Software: PyCharm
import datetime
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

from proxy.proxy import ProxyUtil
from pymysql import DATE, TIMESTAMP
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.mysql import INTEGER
from util.util import Base, r

# class BagumiWorks(Base):
#     __tablename__ = 'bagumi'
#
#     __table_args__ = {
#         'mysql_engine': 'InnoDB',
#         'mysql_charset': 'utf8mb4',
#         'schema': 'bagumi'
#     }
#
#     id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
#     title = Column(String(100), nullable=False)
#     title_chinese = Column(String(100))
#     air_date = Column(DATE, default=None)
#     episodes = Column(INTEGER(unsigned=True), default=0)
#     introduction = Column(Text)
#     score = Column(INTEGER, default=0)
#     address = Column(String(255), nullable=False)
#     rank = Column(INTEGER(unsigned=True))
#     bagumi_id = Column(INTEGER(unsigned=True))
#     votes = Column(INTEGER, default=0)
#     create_time = Column(TIMESTAMP, default=datetime.datetime.now)
#     update_time = Column(TIMESTAMP,
#                          default=datetime.datetime.now,
#                          onupdate=datetime.datetime.now)


class BagumiSpider:
    def __init__(self):
        self.urls_waiting = ['https://bangumi.tv/anime/browser']
        self.urls_already_crawled = []
        self.proxy_util = ProxyUtil()
        self.redis = r

    def url_classify(self):
        i = 0
        while True:
            try:
                # if i == 10:
                #     break
                _, url = self.redis.blpop('bangumi:url:list')
                # print(url)
                if 'browser' in url:
                    self.browser_spider(url)
                elif 'subject' in url:
                    self.subject_spider(url)
                elif 'person' in url:
                    self.person_spider(url)
            except Exception as e:
                print(e)

    def browser_spider(self, url):
        req = self.proxy_util.request_with_proxy(url)
        if req:
            req.encoding = 'utf-8'
            _url_parse = urlparse(url)
            re_req_list = re.findall(
                r'href="(\/(browser|person|subject)\/\d*?)"', req.text)
            for re_req in re_req_list:
                self.add_waiting_url(_url_parse.scheme + "://" +
                                     _url_parse.netloc + re_req[0])

            for l in self.urls_waiting:
                self.add_waiting_url(l)
            # 爬取翻页
            re_req_list = re.findall(r'href="(\?page=\d+)"', req.text)
            for re_req in re_req_list:
                self.add_waiting_url(url + re_req)
            print(f'get person {url}')
        else:
            self.redis.lpush('bangumi:url:list', url)
            print(f'{url} again')

    def subject_spider(self, url):
        req = self.proxy_util.request_with_proxy(url)
        if req:
            req.encoding = 'utf-8'
            _url_parse = urlparse(url)
            re_req_list = re.findall(
                r'href="(\/(browser|person|subject)\/\d*?)"', req.text)
            for re_req in re_req_list:
                self.add_waiting_url(_url_parse.scheme + "://" +
                                     _url_parse.netloc + re_req[0])
            print(f'get person {url}')
        else:
            self.redis.lpush('bangumi:url:list', url)
            print(f'{url} again')

    def person_spider(self, url):
        req = self.proxy_util.request_with_proxy(url)
        if req:
            req.encoding = 'utf-8'
            _url_parse = urlparse(url)
            re_req_list = re.findall(
                r'href="(\/(browser|person|subject)\/\d*?)"', req.text)
            for re_req in re_req_list:
                self.add_waiting_url(_url_parse.scheme + "://" +
                                     _url_parse.netloc + re_req[0])
            print(f'get person {url}')
        else:
            self.redis.lpush('bangumi:url:list', url)
            print(f'{url} again')


    def start(self):
        # 构建待爬列表
        for url in self.urls_waiting:
            self.add_waiting_url(url)

        print('构建待爬列表成功')

        executor = ThreadPoolExecutor(max_workers=10)
        print('多线程爬取开始??')

        ll = [executor.submit(self.url_classify) for _ in range(10)]
        list(as_completed(ll))

    def check_url_by_bl(self, url):
        return self.redis.execute_command(
            f'BF.EXISTS bangumi:crawled:bf {url}')

    def add_waiting_url(self, url):
        # use RedisBloom by docker.  https://github.com/RedisBloom/RedisBloom
        if not self.check_url_by_bl(url):
            try:
                pipe = self.redis.pipeline()
                pipe.execute_command(f'BF.ADD bangumi:crawled:bf {url}')
                pipe.rpush('bangumi:url:list', url)
                pipe.execute()

            except Exception as e:
                print('redis 事务失败')
                raise e
        # else:
        #     print(f'url {url} is already crawled.')


if __name__ == '__main__':
    spider = BagumiSpider()
    # r.flushall()
    spider.start()
    # url = 'https://bagumi.tv/asd21sd'
    # _url_parse = urlparse(url)
    # with open('temp', 'r') as f:
    #     li = re.findall(r'href="(\/(browser|person|subject)\/\d*?)"', f.read())
    #     for l in li:
    #         print(_url_parse.scheme+"://"+_url_parse.netloc+l[0])
    # print(l)

    # re_req_list = re.findall(r'href="(\?page=\d+)"', f.read())
    # for re_req in re_req_list:
    #     # print(re_req)
    #     print(url+re_req)
