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

from lib import mydb
from lib import common


static_offset = 0  # mydb.User を参照するための offset の位置です
user_cursor = None # TODO: Queue.with_cursor が使えないか試してみる


def getcrawluser():
    ''' クロールすべきユーザを取得する '''
    global static_offset

    user = mydb.User.all().fetch(1, static_offset)

    if not user:
        static_offset = 0
        return None

    static_offset += 1
    return user[0]


class FeedbuilderHandler(webapp.RequestHandler):
    ''' Feed 作成についてのリクエストを受け付けます(基本的には cron) '''

    def get(self):
        ''' ユーザのカスタムフィードを作成する '''

        user = getcrawluser()
        if not user:
            common.error(self, 404, 'user not found')
            return

        # ユーザのログがリミットを超えていた場合はその分を削除します
        for log in mydb.Log.all().ancestor(user).order('-time').fetch(1000, offset=mydb.Log._savecount):
            log.delete()

        customfeeds = mydb.CustomFeed.all().ancestor(user).order('time').fetch(1000)
        for cf in customfeeds:
            try:
                ref = fetch(cf.rss_link).content
                soup = Soup(ref)

                dict_compilelist = []
                if cf.item_title_enable:
                    item_titles = common.selectortext(soup, cf.item_title_selector, cf.item_title_attr)
                    dlist_title = [('title', t) for t in item_titles]
                    dict_compilelist.append(dlist_title)

                    message = u"Title 用の要素が %d 個見つかりました" % (len(dlist_title))
                    mydb.Log(feedname=cf.name, type=mydb.Log._types['info'], message=message, parent=user).put()

                if cf.item_link_enable:
                    item_links = common.selectortext(soup, cf.item_link_selector, cf.item_link_attr)
                    dlist_link = [('link', l) for l in item_links]
                    dict_compilelist.append(dlist_link)

                    message = u"Link 用の要素が %d 個見つかりました" % (len(dlist_title))
                    mydb.Log(feedname=cf.name, type=mydb.Log._types['info'], message=message, parent=user).put()

                if cf.item_description_enable:
                    item_descriptions = common.selectortext(soup, cf.item_description_selector, cf.item_description_attr)
                    dlist_description = [('description', d) for d in item_descriptions]
                    dict_compilelist.append(dlist_description)

                    message = u"Description 用の要素が %d 個見つかりました" % (len(dlist_title))
                    mydb.Log(feedname=cf.name, type=mydb.Log._types['info'], message=message, parent=user).put()

                if cf.item_date_enable:
                    item_dates = common.selectortext(soup, cf.item_date_selector, cf.item_date_attr)
                    dlist_date = [('pubdate', dateparser(d)) for d in item_dates]
                    dict_compilelist.append(dlist_date)

                    message = u"Date 用の要素が %d 個見つかりました" % (len(dlist_title))
                    mydb.Log(feedname=cf.name, type=mydb.Log._types['info'], message=message, parent=user).put()

                items = []
                for dl in zip(*dict_compilelist):
                    d = {'title': '', 'link': '', 'description': ''}
                    d.update(dict(dl))
                    items.append(d)

                feeddata = mydb.FeedData.get_by_key_name(cf.name, parent=cf)
                if not feeddata:
                    feeddata = mydb.FeedData(parent=cf, key_name=cf.name)

                feeddata.atom = common.buildfeed('Anon', rsstitle, rsslink, rssdesc, items).decode('UTF-8')
                feeddata.rss = common.buildrss('Anon', rsstitle, rsslink, rssdesc, items).decode('UTF-8')
                feeddata.rdf = common.buildrdf('Anon', rsstitle, rsslink, rssdesc, items).decode('UTF-8')

                if not feeddata.put():
                    raise ValueError  # TODO: save Error

            except:
                message = u"何かエラーが発生しました。"
                log = mydb.Log(feedname=cf.name, type=mydb.Log._types['error'], message=message, parent=user)
                if not log.put():
                    pass  # すみません。 もうどうしようもないです
                raise  # 適切なエラーを定義して正しく登らせるようにする

            else:
                message = u"カスタムフィードの作成に成功しました。"
                log = mydb.Log(feedname=cf.name, type=mydb.Log._types['success'], message=message, parent=user)
                if not log.put():
                    pass  # ログが保存出来なかった場合はどうしようか考えていません。

        
def main():
    url_mapping = [('/feedbuilder', FeedbuilderHandler)]
    application = webapp.WSGIApplication(url_mapping, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

