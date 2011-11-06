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

from lib import moels
from lib import common


class CustomtestHandler(webapp.RequestHandler):
    '''
        カスタムテストの入力を受け付けます
    '''

    def get(self, a):
        '''  '''
        user = common.currentuser()
        if not user:
            common.error(self, 404, "ユーザを確認出来ませんでした。")
            return

        ct = moels.CustomTest.all().ancestor(user).get()
        if not ct:
            ct = moels.CustomTest(parent=user)
            ct.put()

        template_values = {'ct': ct}
        path = os.path.join(os.path.dirname(__file__), 'templates/customtest.html')
        
        self.response.out.write(template.render(path, template_values))


    def post(self, action):
        ''' セレクタの保存と取得を行なっている '''
        if action == 'url':
            self.seturl()

        else :
            user = common.currentuser()

            self.setselectors()

            texts = self.getselectorstexts()
            if texts == False:
                return

            ct = moels.CustomTest.all().ancestor(user).get()

            template_values = {'ct': ct, 'texts': texts}
            path = os.path.join(os.path.dirname(__file__), 'templates/customtest.html')

            self.response.out.write(template.render(path, template_values))


    def seturl(self):
        user = common.currentuser()
        if not user:
            common.error(self, 404, "User not found.")
            return

        ct = moels.CustomTest.all().ancestor(user).get()
        if not ct:
            ct = moels.CustomTest(parent=user)

        ct.setbypost(self.request.POST)

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

        self.redirect('/customtest')
        return

    def setselectors(self):
        ''' Selectors などの設定を保存します '''

        user = common.currentuser()
        if not user:
            common.error(self, 404, "User not found")
            return False

        ct = moels.CustomTest.all().ancestor(user).get()
        if not ct:
            ct = moels.CustomTest(parent=user)

        ct.setbypost(self.request.POST)

        if not ct.put():
            common.error(self, 200, "fail to save.")
            return False

        return True

    def getselectorstexts(self):
        ''' Selectors などの設定から texts を取得します '''

        user = common.currentuser()
        if not user:
            common.error(self, 404, "User not found")
            return False

        ct = moels.CustomTest.all().ancestor(user).get()
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
    url_mapping = [('/customtest(?:/(.+))?', CustomtestHandler)]
    application = webapp.WSGIApplication(url_mapping, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

