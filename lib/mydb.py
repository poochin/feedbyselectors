#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import db


class User(db.Model):
    ''' ユーザの gmail アドレスを保管するだけのエンティティ '''
    user = db.UserProperty()


class Log(db.Model):
    '''
        User の子エンティティ
        ユーザのログを保管します
    '''
    _type_success = 0
    _type_info = 1
    _type_worning = 2
    _type_error = 3

    _savecount = 5

    feedname = db.StringProperty()
    type = db.IntegerProperty()
    message = db.StringProperty(default="")
    time = db.DateTimeProperty(auto_now=True)


class CustomFeed(db.Model):
    '''
        User の子エンティティ
        ユーザのカスタムフィードを保管します
    '''
    name = db.StringProperty()
    time = db.DateTimeProperty(auto_now=True)

    rss_title = db.StringProperty(default="")
    rss_link = db.StringProperty(default="")
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

    def _updatebydict(self, dict):
        self.rss_title = dict['rss_title']
        self.rss_link = dict['rss_link']
        self.rss_description = dict['rss_description']

        self.item_title_enable = bool(dict['item_title_enable'])
        self.item_title_selector = dict['item_title_selector']
        self.item_title_attr = dict['item_title_attr']
        self.item_link_enable = bool(dict['item_link_enable'])
        self.item_link_selector = dict['item_link_selector']
        self.item_link_attr = dict['item_link_attr']
        self.item_description_enable = bool(dict['item_description_enable'])
        self.item_description_selector = dict['item_description_selector']
        self.item_description_attr = dict['item_description_attr']
        self.item_date_enable = bool(dict['item_date_enable'])
        self.item_date_selector = dict['item_date_selector']
        self.item_date_attr = dict['item_date_attr']


class FeedData(db.Model):
    '''
        カスタムフィードを元に作成したフィードのデータ
    '''
    feed = db.TextProperty()
    time = db.DateTimeProperty(auto_now=True)

