#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.ext.db import djangoforms
from google.appengine.api.validation import ValidationError

import defines


class User(db.Model):
    '''User(db.Model)

    各エンティティをユーザが保持する為のルートエンティティです
    '''
    user = db.UserProperty(required=True)


class Log(db.Model):
    '''Log(db.Model)

    問題が生じた際に問題を推測、理解できるように各ユーザ個別のログ
    '''
    def valid_feedname(name):
        if name == None: return
        if len(name) == 0: return
    
        if not re.search('^[A-Za-z]+$', name):
            raise ValueError

    _types = {'success': 0, 'info': 1, 'worning': 2, 'error': 3}
    _savecount = 100

    feedname = db.StringProperty(validator=valid_feedname, required=True)
    type = db.IntegerProperty(choices=_types.values(), required=True)
    message = db.StringProperty(default="")
    time = db.DateTimeProperty(auto_now=True)


class AbstractCustomFeed(polymodel.PolyModel):
    '''AbstractCustomFeed(polymodel.PolyModel)

    ユーザがカスタムフィードを保持する為の基底クラスです
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

    name = db.StringProperty(required=True, validator=valid_feedname)
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
    '''CustomFeed(AbstractCustomFeed)''' 
    pass


class CustomTest(AbstractCustomFeed):
    '''CustomTest(AbstractCustomFeed)

    ユーザが個人的に実験する為のエンティティです
    '''
    def valid_customdata(data):
        if data == None: return
    
        if len(data) >= (300 * 1024):
            raise ValueError, "データサイズが大きすぎます"

    data = db.TextProperty(default=defines.defaulttesthtml, validator=valid_customdata)


class FeedData(db.Model):
    '''FeedData(db.Model)

    カスタムフィードを元に作成した各フィードを保持します
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


