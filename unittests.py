#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Original Code:
#   http://d.hatena.ne.jp/griefworker/20100215/google_app_engine_python_unittest
#

import os
import sys
import pwd


# 環境設定
# これをしないと GAE のモジュールをインポートできない。
# テスト対象のクラスも同様。

# ここを自分の環境に合わせて書き変えます
USER_ID = os.getuid()
HOME_DIR = os.path.join('/home', pwd.getpwuid(USER_ID)[0])
GAE_HOME = os.path.join(HOME_DIR, 'lib', 'google_appengine')
PROJECT_HOME = os.path.join(HOME_DIR, 'git', 'feedbyselectors')

# テストで使う GAE のモジュールのパスを作成
EXTRA_PATHS = [
    GAE_HOME,
    PROJECT_HOME,
    os.path.join(GAE_HOME, 'google', 'appengine', 'api'),
    os.path.join(GAE_HOME, 'google', 'appengine', 'ext'),
    os.path.join(GAE_HOME, 'lib', 'yaml', 'lib'),
    os.path.join(GAE_HOME, 'lib', 'webob'),
]

# パスを追加する。
sys.path = EXTRA_PATHS + sys.path


import unittest

# スタブをインポート
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.api import user_service_stub
from google.appengine.api import users
from google.appengine.ext import db

from BeautifulSoup import BeautifulSoup as Soup

# テスト対象のクラスをインポート
from lib import mydb
from lib import common
from lib import defines


APP_ID = u"test_id"
AUTH_DOMAIN = "gmail.com"
LOGGED_IN_USER = "test@example.com"


posts = {'name': u'test', 'data': defines.defaulttesthtml,
    u'rss_title': u'Test data', u'rss_link': u'http://example.com/', u'rss_description': u'Description', 
    'item_title_enable': True, 'item_title_selector': u'.section h3', 'item_title_attr': u'',
    'item_link_enable': True, 'item_link_selector': u'.section h3 a', 'item_link_attr': u'href',
    'item_description_enable': True, 'item_description_selector': u'.section .desc', 'item_description_attr': u'',
    'item_date_enable': True, 'item_date_selector': u'.date', 'item_date_attr': u''}


# 単体テストのベースクラス
class GAETestBase(unittest.TestCase):

    # ベースクラスの setUp 内でスタブを登録しておく
    def setUp(self):
        # API Proxy を登録
        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()

        # Datastore のスタブを登録
        stub = datastore_file_stub.DatastoreFileStub(APP_ID,
                '/dev/null',
                '/dev/null')
        apiproxy_stub_map.apiproxy.RegisterStub("datastore_v3", stub)

        # APPLICATION_ID の設定
        # これを忘れると Datastore がエラーを出す
        os.environ["APPLICATION_ID"] = APP_ID

        # UserService のスタブを登録
        apiproxy_stub_map.apiproxy.RegisterStub("user",
                user_service_stub.UserServiceStub())
        os.environ["AUTH_DOMAIN"] = AUTH_DOMAIN
        os.environ["USER_EMAIL"] = LOGGED_IN_USER


class UserTest(GAETestBase):
    ''' ユーザの登録テスト '''
    def testUser(self):
        mydb.User(user=users.User('test@gmail.com')).put()
        self.assertEqual(1, mydb.User.all().count())


class LogTest(GAETestBase):
    ''' '''
    def testLog(self):
        user = mydb.User(user=users.User('test@gmail.com'))
        user.put()

        log = mydb.Log(parent=user, feedname='test', type=mydb.Log._types['success'], message=u'テスト')
        log.put()

        self.assertEqual(1, mydb.Log.all().ancestor(user).count())


class CustomFeedTest(GAETestBase):
    ''' '''
    def testFeed(self):
        user = mydb.User(user=users.User('test@gmail.com'))
        user.put()

        feed = mydb.CustomFeed(parent=user, name=u'test')
        feed.setbypost(posts)
        feed.put()

        cf = mydb.CustomFeed.all().ancestor(user).get()
        feeddict = dict((key, getattr(feed, key)) for key in feed.properties() if posts.has_key(key))

        d = dict((key, posts[key]) for key in cf.properties() if posts.has_key(key))
        self.assertEqual(d, feeddict)


class CustomTestTest(GAETestBase):
    ''' '''
    def testCustomTest(self):
        user = mydb.User(user=users.User('test@gmail.com'))
        user.put()

        feed = mydb.CustomTest(parent=user, name=u'test')
        feed.setbypost(posts)
        feed.put()

        cf = mydb.CustomFeed.all().ancestor(user).get()
        feeddict = dict((key, getattr(feed, key)) for key in feed.properties() if posts.has_key(key))

        self.assertEqual(posts, feeddict)


class FeedDataTest(GAETestBase):
    ''' '''
    def testFeedData(self):
        user = mydb.User(user=users.User('test@gmail.com'))
        user.put()

        feed = mydb.CustomFeed(parent=user, name=u'test')
        feed.setbypost(posts)
        feed.put()

        soup = Soup(defines.defaulttesthtml)
        titles = common.selectortext(soup, posts['item_title_selector'], posts['item_title_attr'])
        links = common.selectortext(soup, posts['item_link_selector'], posts['item_link_attr'])
        descriptions = common.selectortext(soup, posts['item_description_selector'], posts['item_description_attr'])
 
        items = [dict([('title', t), ('link', l), ('description', d)]) for t, l, d in zip(titles, links, descriptions)]
        rss_title = posts['rss_title'].encode('UTF-8')
        rss_link = posts['rss_link'].encode('UTF-8')
        rss_description = posts['rss_description'].encode('UTF-8')

        fd = mydb.FeedData(parent=feed)
        fd.atom = common.buildatom('Anon', rss_title, rss_link, rss_description, items)
        if common.django.VERSION < (1, 1, 5):
            # django <= 1.1.4 でなければ RSS と RDF の作成時にエラーが出る
            fd.rss = common.buildrss('Anon', posts['rss_title'], posts['rss_link'], posts['rss_description'], items)
            fd.rdf = common.buildrdf('Anon', posts['rss_title'], posts['rss_link'], posts['rss_description'], items)
        fd.put()

        self.assertEqual(1, mydb.FeedData.all().ancestor(user).count())


if __name__ == '__main__':
    unittest.main()

