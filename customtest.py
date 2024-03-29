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
from cgi import escape
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch

from lib.BeautifulSoup import BeautifulSoup as Soup

from lib import models
from lib import common
from lib import defines


class CustomtestHandler(webapp.RequestHandler):
    '''CustomtestHandler(webapp.RequestHandler)

    ユーザによるフィード作成のテスト環境を提供します
    '''
    def get(self):
        user = common.currentuser()
        if not user:
            common.error(self, 404, "ユーザを確認出来ませんでした。")
            return

        ct = models.CustomTest.all().ancestor(user).get()
        if not ct:
            ct = models.CustomTest(name='custom', parent=user)
            ct.put()

        template_values = {'ct': ct}
        path = os.path.join(os.path.dirname(__file__), 'templates/customtest.html')
        
        self.response.out.write(template.render(path, template_values))

    def post(self, action=None):
        ''' セレクタの保存と取得を行なっている '''
        if action == 'url':
            self.seturl()
            self.redirect('/customtest')

        else :
            user = common.currentuser()

            self.setselectors()

            texts = self.getselectorstexts()
            if texts == False:
                return

            ct = models.CustomTest.all().ancestor(user).get()

            template_values = {'ct': ct, 'texts': texts}
            path = os.path.join(os.path.dirname(__file__), 'templates/customtest.html')

            self.response.out.write(template.render(path, template_values))

    def seturl(self):
        '''URLとURLからフェッチして保存します'''
        user = common.currentuser()
        if not user:
            common.error(self, 404, "User not found.")
            return

        ct = models.CustomTest.all().ancestor(user).get()
        if not ct:
            ct = models.CustomTest(parent=user)

        ct.setbypost(self.request.POST)

        if not ct.rss_link:
            soup = Soup(defines.defaulttesthtml)
        else:
            result = urlfetch.fetch(ct.rss_link)
            if result.status_code != 200:
                common.error(self, 200, "Url Fetch Error")
                return
            soup = Soup(result.content)

        try: 
            ct.data = soup.prettify().decode('UTF-8')
        except ValueError, message:
            common.error(self, 200, message)
            return
            
        if not ct.put():
            common.error(self, 200, 'fail to save')
            return

    def setselectors(self):
        '''POSTデータをカスタムテストエンティティに保存します'''
        user = common.currentuser()
        if not user:
            common.error(self, 404, "User not found")
            return False

        ct = models.CustomTest.all().ancestor(user).get()
        if not ct:
            ct = models.CustomTest(parent=user)

        ct.setbypost(self.request.POST)

        if not ct.put():
            common.error(self, 200, "fail to save.")
            return False

        return True

    def getselectorstexts(self):
        '''カスタムテストエンティティのセレクタ属性セットから各テキストを取得します'''
        user = common.currentuser()
        if not user:
            common.error(self, 404, "User not found")
            return False

        ct = models.CustomTest.all().ancestor(user).get()
        if not ct:
            return False

        soup = Soup(ct.data)

        texts = {}
        if ct.item_title_enable and ct.item_title_selector:
            texts['titles'] = common.selectortext(soup, ct.item_title_selector, ct.item_title_attr)
        if ct.item_link_enable and ct.item_link_selector:
            texts['links'] = common.selectortext(soup, ct.item_link_selector, ct.item_link_attr)
        if ct.item_description_enable and ct.item_description_selector:
            texts['descriptions'] = common.selectortext(soup, ct.item_description_selector, ct.item_description_attr)
        if ct.item_date_enable and ct.item_date_selector:
            texts['dates'] = common.selectortext(soup, ct.item_date_selector, ct.item_date_attr)

        return texts
           

def main():
    url_mapping = [
        ('/customtest', CustomtestHandler),
        ('/customtest/(.+)', CustomtestHandler)
    ]
    application = webapp.WSGIApplication(url_mapping, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

