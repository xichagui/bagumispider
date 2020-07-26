# -*- coding: utf-8 -*-
# @Time    : 2020/7/20 18:59
# @Author  : Xichagui
# @Site    :
# @File    : util.py
# @Software: PyCharm
import threading

import pymysql


class Db:
    def __init__(self, database):
        self.conn = None
        self.mysql_host = '127.0.0.1'
        self.mysql_user = 'root'
        self.mysql_pw = '123456'
        self.mysql_charset = 'utf8mb4'
        self.lock = threading.Lock()
        self.table_name = None
        self.database = database
        self.get_conn(database)


    def get_conn(self, database: str):
        try:
            self.db = self.conn = pymysql.connect(
                host=self.mysql_host,
                user=self.mysql_user,
                password=self.mysql_pw,
                db=database,
                charset=self.mysql_charset,
            )
            self.cursor = self.db.cursor()
            self.select_db()
        except pymysql.OperationalError as e:
            print(e)
            if self.create_database(database):
                self.get_conn(database)
            else:
                self.db = False
                self.cursor = None
        except pymysql.ProgrammingError as e:
            print(e)
            with open('table.sql','r') as f:
                self.create_table(f.read())


    def create_database(self, database):
        db = pymysql.connect(
            host=self.mysql_host,
            user=self.mysql_user,
            password=self.mysql_pw,
            charset=self.mysql_charset,
        )
        sql = f'create database if not exists {database}'
        try:
            with db.cursor() as cur:
                cur.execute(sql)
                print(f'Create database {database} success.')
                return True
        except Exception:
            print(f'Create database {database} error.')
            return False

    def create_table(self, sql: str):
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql)
                print('Create table success!')
            return True
        except Exception as e:
            print(e)
            return False

    def insert_db(self, sql: str):
        self.lock.acquire()
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql)
                self.db.commit()
                self.lock.release()
                return True
        except Exception as e:
            self.lock.release()
            self.db.rollback()
            return False

    def select_db(self, sql=None):
        try:
            if sql:
                res = self.cursor.execute(sql)
            else:
                sql = f'select 1 from {self.table_name} limit 1;'
                res = self.cursor.execute(sql)
            return res
        except Exception as e:
            print('Table is not exists.')
            raise e


if __name__ == '__main__':
    db = Db('bagumi')
    # print(db.select_all())
