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

from lib.BeautifulSoup import BeautifulSoup as Soup
from lib.soupselect import select
from lib import common
from lib import defines


class TestpageHandler(webapp.RequestHandler):
    ''' Testpage のリクエストを受け付けています '''

    def get(self):
        ''' Testpage を標準状態で出力します '''

        template_values = {'code': escape(defines.defaulttesthtml),}
        path = os.path.join(os.path.dirname(__file__), 'templates/testpage.html')

        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        ''' Testpage についてセレクタと属性の入力があった場合 '''

        raw_selector = self.request.get('selector')
        selector = escape(raw_selector, '"')
        raw_attr = self.request.get('attr')
        attr = escape(raw_attr, '"')

        soup = Soup(defines.defaulttesthtml)
        texts = common.selectortext(soup, selector, attr)
        
        template_values = {'code': escape(defines.defaulttesthtml),
            'selector': selector, 'attr': attr,
            'results': texts,}
        path = os.path.join(os.path.dirname(__file__), 'templates/testpage.html')

        self.response.out.write(template.render(path, template_values))


def main():
    url_mapping = [('/testpage', TestpageHandler)]
    application = webapp.WSGIApplication(url_mapping, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

