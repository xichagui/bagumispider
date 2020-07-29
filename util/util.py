# -*- coding: utf-8 -*-
# @Time    : 2020/7/20 18:59
# @Author  : Xichagui
# @Site    :
# @File    : util.py
# @Software: PyCharm
import threading

import pymysql
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# 初始化数据库连接:
from sqlalchemy_utils import create_database, database_exists

DATABASE_ENGINE = 'mysql+pymysql'
DATABASE_USER = 'root'
DATABASE_PW = '123456'
DATABASE_IP = 'localhost:3306'
PROXY_DATABASE = 'proxy'

DATABASE_URL = f'{DATABASE_ENGINE}://{DATABASE_USER}:{DATABASE_PW}@{DATABASE_IP}'

engine = create_engine(f'{DATABASE_URL}/{PROXY_DATABASE}', echo=False)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
Base = declarative_base()
session = DBSession()


def check_database(database):
    if not database_exists(f'{DATABASE_URL}/{database}'):
        database_url = f'{DATABASE_URL}/{database}'
        create_database(database_url)


check_database(PROXY_DATABASE)


def init_db():
    Base.metadata.create_all(engine)
