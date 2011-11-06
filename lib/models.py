#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.ext.db import djangoforms
from google.appengine.api.validation import ValidationError

import defines


class User(db.Model):
    ''' ユーザの gmail アドレスを保管するだけのエンティティ '''
    user = db.UserProperty()


class Log(db.Model):
    '''
        User の子エンティティ
        ユーザのログを保管します
    '''
 
    def valid_feedname(name):
        if name == None: return
        if len(name) == 0: return
    
        if not re.search('^[A-Za-z]+$', name):
            raise ValueError

    _types = {'success': 0, 'info': 1, 'worning': 2, 'error': 3}
    _savecount = 100

    feedname = db.StringProperty(validator=valid_feedname)
    type = db.IntegerProperty(choices=_types.values())
    message = db.StringProperty(default="")
    time = db.DateTimeProperty(auto_now=True)


class AbstractCustomFeed(polymodel.PolyModel):
    '''
        カスタムフィードの抽象型
        ユーザのカスタムフィードを保管します
    '''
    def valid_feedname(name):
        if name == None: return
        if len(name) == 0: return
    
        if re.search('[^A-Z^a-z]', name):
            raise ValueError

    def valid_url(url):
        if url == None: return
        if len(url) == 0: return
    
        if not re.match('https?://', url):
            raise ValueError

    name = db.StringProperty(validator=valid_feedname)
    time = db.DateTimeProperty(auto_now=True)

    rss_title = db.StringProperty(default="")
    rss_link = db.StringProperty(default="", validator=valid_url)
    rss_description = db.StringProperty(default="")

    item_title_enable = db.BooleanProperty(default=True)
    item_title_selector = db.StringProperty(default="")
    item_title_attr = db.StringProperty(default="")
    item_link_enable = db.BooleanProperty(default=True)
    item_link_selector = db.StringProperty(default="")
    item_link_attr = db.StringProperty(default="")
    item_description_enable = db.BooleanProperty(default=True)
    item_description_selector = db.StringProperty(default="")
    item_description_attr = db.StringProperty(default="")
    item_date_enable = db.BooleanProperty(default=False)
    item_date_selector = db.StringProperty(default="")
    item_date_attr = db.StringProperty(default="")

    def setbypost(self, post):
        for key in self.properties():
            if post.has_key(key):
                if isinstance(getattr(self, key), bool):
                    setattr(self, key, bool(post[key]))
                else:
                    setattr(self, key, post[key])


class CustomFeed(AbstractCustomFeed):
    '''
        カスタムフィード
        ユーザのフィード設定を保管します
    '''
    pass


class CustomTest(AbstractCustomFeed):
    '''
        カスタムテスト
        ユーザによるテストの設定を保管します
    '''
    def valid_customdata(data):
        if data == None: return
    
        if len(data) >= (300 * 1024):
            raise ValueError, "データサイズが大きすぎます"

    data = db.TextProperty(default=defines.defaulttesthtml, validator=valid_customdata)


class FeedData(db.Model):
    '''
        カスタムフィードを元に作成したフィードのデータ
    '''
    def valid_feed(f):
        if f == None: return
        if len(f) == 0: return

        if len(f) >= (100 * 1024):
            raise ValueError

    atom = db.TextProperty(default="", validator=valid_feed)
    rss = db.TextProperty(default="", validator=valid_feed)
    rdf = db.TextProperty(default="", validator=valid_feed)
    time = db.DateTimeProperty(auto_now=True)


