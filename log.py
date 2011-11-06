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
from lib import models


class LogviewHandler(webapp.RequestHandler):
    ''' ユーザによるログの閲覧リクエストを受け付けています '''

    def get(self):
        ''' ログを閲覧します '''
        user = common.currentuser()
        if not user:
            common.error(self, 404, "User not found.")
            return

        logs = models.Log.all().order('-time').ancestor(user).fetch(1000)

        template_values = {'logs': logs}
        path = os.path.join(os.path.dirname(__file__), 'templates/log.html')

        self.response.out.write(template.render(path, template_values))


def main():
    url_mapping = [('/log', LogviewHandler)]
    application = webapp.WSGIApplication(url_mapping, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
