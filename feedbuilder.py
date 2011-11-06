#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import time
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api.urlfetch import fetch

from lib.BeautifulSoup import BeautifulSoup as Soup
from lib.dateutil.parser import parse as dateparser

from lib import models
from lib import common


user_cursor = None

def nextusermodel():
    '''nextusermodel()
    
    ユーザのイテレーションし次の対象ユーザを返します
    '''
    global user_cursor

    query = models.User.all()
    if user_cursor:
        query.with_cursor(cursor)
    user = query.get()
    user_cursor = query.cursor() if user else None
    return user


class FeedbuilderHandler(webapp.RequestHandler):
    '''FeedbuilderHandler(webapp.RequestHandler)

    ユーザのカスタムフィードを元に各フィードを作成します
    '''

    def get(self):
        user = nextusermodel()
        if not user:
            common.error(self, 404, 'user not found')
            return

        for log in models.Log.all().ancestor(user).order('-time').fetch(1000, offset=models.Log._savecount):
            log.delete()

        customfeeds = models.CustomFeed.all().ancestor(user).order('time')
        for cf in customfeeds:
            if not cf.rss_link:
                continue

            ref = fetch(cf.rss_link).content
            soup = Soup(ref)

            dict_compilelist = []

            if cf.item_title_enable:
                titles = common.selectortext(soup, cf.item_title_selector, cf.item_title_attr)
                dlist_title = [('title', t) for t in titles]
                dict_compilelist.append(dlist_title)
            
            if cf.item_link_enable:
                links = common.selectortext(soup, cf.item_link_selector, cf.item_link_attr)
                dlist_link = [('link', l) for l in links]
                dict_compilelist.append(dlist_link)

            if cf.item_description_enable:
                descriptions = common.selectortext(soup, cf.item_description_selector, cf.item_description_attr)
                dlist_description = [('description', d) for d in descriptions]
                dict_compilelist.append(dlist_description)

            if cf.item_date_enable:
                dates = common.selectortext(soup, cf.item_date_selector, cf.item_date_attr)
                dlist_date = [('pubdate', dateparser(d)) for d in dates]
                dict_compilelist.append(dlist_date)

            message = u'title %d 個, link %d 個, description %d 個, dates %d 個 見つかりました。' % (
                len(titles), len(links), len(descriptions), len(dates))
            models.Log(feedname=cf.name, type=model.Log._types['info'], message=message, parent=user).put()

            items = []
            for dl in zip(*dict_compilelist):
                d = {'title': '', 'link': '', 'description': ''}
                d.update(dict(dl))
                items.append(d)

            feeddata = models.FeedData.get_by_key_name(cf.name, parent=cf)
            if not feeddata:
                feeddata = models.FeedData(parent=cf, key_name=cf.name)

            try:
                rss_title = cf.rss_title.encode('UTF-8')
                rss_link = cf.rss_link.encode('UTF-8')
                rss_description = cf.rss_description.encode('UTF-8')
    
                feeddata.atom = common.buildatom('Anon', rss_title, rss_link, rss_description, items).decode('UTF-8')
                feeddata.rss = common.buildrss('Anon', rss_title, rss_link, rss_description, items).decode('UTF-8')
                feeddata.rdf = common.buildrdf('Anon', rss_title, rss_link, rss_description, items).decode('UTF-8')

                if not feeddata.put():
                    raise ValueError  # TODO: save Error
            except:
                message = u"何かエラーが発生しました。"
                models.Log(feedname=cf.name, type=models.Log._types['error'], message=message, parent=user).put()
                raise

            else:
                message = u"カスタムフィードの作成に成功しました。"
                models.Log(feedname=cf.name, type=models.Log._types['success'], message=message, parent=user).put()

        
def main():
    url_mapping = [('/feedbuilder', FeedbuilderHandler)]
    application = webapp.WSGIApplication(url_mapping, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

