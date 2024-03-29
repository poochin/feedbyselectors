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

from lib import common


class StaticpageHandler(webapp.RequestHandler):
    '''
        静的なページについてのリクエストを受け付けます。
        base.html > custom.html > (static).html とする事で、他と同様のレイアウトを実現します。
    '''
    def get(self, pagename='index'):
        ''' 静的なページの出力 '''
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'templates/%s.html' % (pagename))

        if not os.path.exists(path):
            common.error(self, 404, "Page not found.")
            return

        self.response.out.write(template.render(path, template_values))


def main():
    url_mapping = [
        ('/(?:index)?', StaticpageHandler),
    ]
    application = webapp.WSGIApplication(url_mapping ,debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

