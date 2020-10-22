# -*- coding: utf-8 -*-
# @Time    : 2020/7/20 18:59
# @Author  : Xichagui
# @Site    :
# @File    : util.py
# @Software: PyCharm

import redis
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
# 初始化数据库连接:
from sqlalchemy_utils import create_database, database_exists

DATABASE_ENGINE = 'mysql+pymysql'
DATABASE_USER = 'root'
DATABASE_PW = '123456'
DATABASE_IP = 'localhost:3306'
PROXY_DATABASE = 'proxy'

DATABASE_URL = f'{DATABASE_ENGINE}://{DATABASE_USER}:{DATABASE_PW}@{DATABASE_IP}'

engine = create_engine(f'{DATABASE_URL}/{PROXY_DATABASE}', echo=False, pool_size=20)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
Base = declarative_base()
Session = scoped_session(DBSession)

#redis连接池
redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0, decode_responses=True)
r = redis.StrictRedis(connection_pool=redis_pool)


def check_database(database):
    if not database_exists(f'{DATABASE_URL}/{database}'):
        database_url = f'{DATABASE_URL}/{database}'
        create_database(database_url)


check_database(PROXY_DATABASE)


def init_db():
    Base.metadata.create_all(engine)
