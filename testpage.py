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


# このページで探索対象として使用する html
# 外部の html を読み込むようにはしない
# TODO: 子孫セレクタと子セレクタの違いを判別させられるようなコードを追加する
html = '''\
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />
        <title>The title</title>
        <link rel="stylesheet" href="main.css" type="text/css"/>
    </head>
    <body>
        <h1>Test Page</h1>
        <nav>
            <ul>
                <li><a href="/index.html">Home</a></li>
                <li><a href="/about.html">About</a></li>
                <li><a href="/download.html">Download</a></li>
            </ul>
        </nav>
        <div id="contain">
            <h2>最新の更新情報</h2>
            <div class="section">
                <h3><a href="/board.php?date=1970-01-01">Hello, World!</a></h3>
                <p class="desc">The Unix epoch time starting.</p>
            </div>
            <div class="section">
                <h3><a href="/board.php?date=1995-09-24">Releasing Windows 95.</a></h3>
                <p class="desc">Microsoft Corp. released Windows95.</p>
            </div>
            <div class="section">
                <h3><a href="/board.php?date=2011-10-04">Publish iPhone 4S</a></h3>
                <p class="desc">Apple Inc. Published iPhone 4S.</p>
            </div>
        </div>
        <footer>
            <address>@poochin</address>
        </footer>
    </body>
</html>
'''


class TestpageHandler(webapp.RequestHandler):
    ''' Testpage のリクエストを受け付けています '''

    def get(self):
        ''' Testpage を標準状態で出力します '''

        template_values = {'code': escape(html),}
        path = os.path.join(os.path.dirname(__file__), 'templates/testpage.html')

        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        ''' Testpage についてセレクタと属性の入力があった場合 '''

        raw_selector = self.request.get('selector')
        selector = escape(raw_selector, '"')
        raw_attr = self.request.get('attr')
        attr = escape(raw_attr, '"')

        soup = Soup(html)
        texts = common.selectortext(soup, selector, attr)
        
        template_values = {'code': escape(html),
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

