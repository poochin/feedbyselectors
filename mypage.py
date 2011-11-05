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


import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

from google.appengine.api.users import User
from google.appengine.ext import db

from lib import mydb
from lib import common


class MypageHandler(webapp.RequestHandler):
    ''' ユーザによる自分のマイページに対するリクエストを受け付けます '''

    def get(self):
        ''' ユーザのマイページを表示します '''

        user = common.currentuser()
        if not user:
            common.error(self, 404, 'ユーザが見つかりませんでした。')

        myfeeds = mydb.CustomFeed.all().ancestor(user).fetch(1000)
        template_values = {'username': user.user, 'userid': user.key().id(), 'feeds': myfeeds}
        path = os.path.join(os.path.dirname(__file__), 'templates/mypage.html')

        self.response.out.write(template.render(path, template_values))


class NewfeedHandler(webapp.RequestHandler):
    ''' 新しいカスタムフィードの作成のリクエストを受け付けます '''

    def get(self):
        ''' 不正なリクエスト '''
        pass

    def post(self):
        ''' 新カスタムフィードの更新の申請'''
        user = common.currentuser()

        newfeedname = self.request.POST['name']
        if mydb.CustomFeed.get_by_key_name(newfeedname, parent=user):
            common.error(self, 409, "ページが既に存在します。")
            return

        cf = mydb.CustomFeed(parent=user, key_name=newfeedname, name=newfeedname)
        if not cf.put():
            common.error(self, 400, "フィードの作成に失敗しました。")
            return

        self.redirect("/mypage")


class DeletefeedHandler(webapp.RequestHandler):
    ''' カスタムフィードの削除のリクエストを受け付けます '''
    def get(self):
        ''' 不正なリクエストです '''
        pass

    def post(self):
        user = common.currentuser()

        feedname = self.request.POST['name']
        cf = mydb.CustomFeed.get_by_key_name(feedname, parent=user)
        if not cf:
            common.error(self, 400, "ページは存在しません。")
            return

        cf.delete()
        if cf.is_saved():
            common.error(self, 400, "削除に失敗しました。")
            return

        self.redirect('/mypage')


def main():
    url_mapping = [
        ('/mypage', MypageHandler),
        ('/mypage/newfeed', NewfeedHandler),
        ('/mypage/deletefeed', DeletefeedHandler),
    ]
    application = webapp.WSGIApplication(url_mapping, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

