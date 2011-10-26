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

from lib import mydb
from lib import common


class EditHandler(webapp.RequestHandler):
    ''' Edit ページへのリクエストを受け付けています '''
    def get(self, feedname):
        ''' Edit ページを表示します '''
        u = common.currentuser()
        if not u:
            common.error(self, 404, 'not accept user')
            return

        cf = mydb.CustomFeed.get_by_key_name(feedname, parent=u)
        if not cf:
            common.error(self, 404, "フィードが存在しません。");
            return

        udict = {}
        for attr in ("rss_title", "rss_link", "rss_description", 
            "item_title_enable", "item_title_selector", "item_title_attr",
            "item_link_enable", "item_link_selector", "item_link_attr",
            "item_description_enable", "item_description_selector", "item_description_attr",
            "item_date_enable", "item_date_selector", "item_date_attr"):
            value = getattr(cf, attr, "")
            if isinstance(value, bool):
                udict[attr] = value
            else:
                udict[attr] = escape(value, '"')


        template_values = {'feedname': feedname}
        template_values.update(udict)
        path = os.path.join(os.path.dirname(__file__), 'templates/edit.html')

        self.response.out.write(template.render(path, template_values))

    def post(self, feedname):
        ''' Edit ページの更新を行います '''
        u = common.currentuser()
        if not u:
            common.error(self, 404, 'not accept user')
            return

        feed = mydb.CustomFeed.get_by_key_name(feedname, parent=u)
        if not feed:
            self.error(self, 404, 'Feed not found')

        raw_values = {
            "rss_title": self.request.get('rss_title'),
            "rss_link": self.request.get('rss_link'),
            "rss_description": self.request.get('rss_description'),
            "item_title_enable": self.request.get('item_title_enable'),
            "item_title_selector": self.request.get('item_title_selector'),
            "item_title_attr": self.request.get('item_title_attr'),
            "item_link_enable": self.request.get('item_link_enable'),
            "item_link_selector": self.request.get('item_link_selector'),
            "item_link_attr": self.request.get('item_link_attr'),
            "item_description_enable": self.request.get('item_description_enable'),
            "item_description_selector": self.request.get('item_description_selector'),
            "item_description_attr": self.request.get('item_description_attr'),
            "item_date_enable": self.request.get('item_date_enable'),
            "item_date_selector": self.request.get('item_date_selector'),
            "item_date_attr": self.request.get('item_date_attr'),
        }
        values = dict([(k, escape(v, '"')) for k, v in raw_values.iteritems()])

        feed._updatebydict(raw_values)

        if feed.put():
            self.redirect('/edit/' + feedname)
        else:
            common.error(self, 200, "fail to save.")
            return

        template_values = {'feedname': feedname}
        template_values.update(values)
        path = os.path.join(os.path.dirname(__file__), 'templates/edit.html')

        self.response.out.write(template.render(path, template_values))


def main():
    url_mapping = [('/edit/(.+)', EditHandler)]
    application = webapp.WSGIApplication(url_mapping, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

