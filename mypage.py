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

from lib import models
from lib import common


class MypageHandler(webapp.RequestHandler):
    '''MypageHandler(webapp.RequestHandler)

    ユーザのマイページを表示します
    '''
    def get(self):
        user = common.currentuser()
        if not user:
            common.error(self, 404, 'ユーザが見つかりません')
            return

        myfeeds = [models.CustomFeed.all().ancestor(user)]
        template_values = {'username': user.user, 'userid': user.key().id(), 'feeds': myfeeds}
        path = os.path.join(os.path.dirname(__file__), 'templates/mypage.html')

        self.response.out.write(template.render(path, template_values))


class NewfeedHandler(webapp.RequestHandler):
    '''NewfeedHandler(webapp.RequestHandler)

    カスタムフィードを作成します
    '''
    def post(self):
        user = common.currentuser()
        if not user:
            common.error(self, 404, 'ユーザが見つかりません')

        newfeedname = self.request.POST['name']
        if models.CustomFeed.get_by_key_name(newfeedname, parent=user):
            common.error(self, 409, "既にページが存在します。")
            return

        cf = models.CustomFeed(parent=user, key_name=newfeedname, name=newfeedname)
        if not cf.put():
            common.error(self, 400, "フィードの作成に失敗しました。")
            return

        self.redirect("/mypage")


class DeletefeedHandler(webapp.RequestHandler):
    '''DeletefeedHandler(webapp.RequestHandler)

    カスタムフィードを削除します
    '''
    def post(self):
        user = common.currentuser()
        if not user:
            common.error(self, 404, 'ユーザが見つかりません')
            return

        feedname = self.request.POST['name']
        cf = models.CustomFeed.get_by_key_name(feedname, parent=user)
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

