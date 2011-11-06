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
from cgi import escape

from lib import common
from lib import models


class FeedHandler(webapp.RequestHandler):
    ''' FeedHandler(webapp.RequestHandler)
    
    FeedHandler はユーザIDとフィード名、そしてまたはフィードタイプの入力を得て値を返します。
    '''
    def get(self, userid, feedname, feedtype=None):

        user = models.User.get_by_id(int(userid))
        if not user:
            common.error(self, 404, 'User ID is not found.')
            return

        cf = models.CustomFeed.get_by_key_name(feedname, parent=user)
        if not cf:
            common.error(self, 404, 'CutomFeed is not found.')
            return
        
        feed = models.FeedData.get_by_key_name(feedname, parent=cf)
        if not feed:
            common.error(self, 404, 'Feed data is not found.')
            return

        if feedtype == None:
            template_values = {'userid': userid, 'cf': cf, 'nickname': ''}
            path = os.path.join(os.path.dirname(__file__), 'templates/feed.html')

            self.response.out.write(template.render(path, template_values))

        else: 
            self.response.out.write(getattr(feed, feedtype))


def main():
    url_mapping = [('/feed/(\d+)/([a-zA-Z]+)(?:/(atom|rss|rdf))?', FeedHandler)]
    application = webapp.WSGIApplication(url_mapping, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

