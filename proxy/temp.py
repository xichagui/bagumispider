# -*- coding: utf-8 -*-
# @Time    : 2020/8/17 15:15
# @Author  : Xichagui
# @Site    : 
# @File    : temp.py
# @Software: PyCharm


import datetime
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse


# l = [0] * 5
l2 = [0] * 5
def start():
    t = ThreadPoolExecutor(max_workers=5)
    l = [t.submit(fun1, i) for i in range(5)]
    list(as_completed(l))
    print('ok')

def fun1(i):
    print(111)


    try:
        t2 = ThreadPoolExecutor(max_workers=5)
        l2 = [t2.submit(fun2) for _ in range(5)]
        list(as_completed(l2))
        # time.sleep(11)
        print(i)
    except Exception as e:
        print(e)
    # time.sleep(5)


def fun2():
    print(222)


if __name__ == '__main__':
    start()