#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from google.appengine.api.users import User
from google.appengine.ext.webapp import template

import mydb
from soupselect import select


def error(handler, no, message="Fail to load."):
    ''' エラー用の画面を出力します。 '''
    handler.error(no)
    path = os.path.join(os.path.dirname(__file__), '../templates/error.html')
    handler.response.out.write(template.render(path, {'error_message': message}))


def currentuser():
    ''' 現在のログインユーザを取得して返します。 '''
    user = User()
    u = mydb.User.all().filter('user =', user).get()
    if not u:
        u = mydb.User(user=user)
        u.put()
        if not u.is_saved():
            return None
    return u


def selectortext(soup, selector, attr):
    ''' dom object に対して selector で抽出した後、目的の属性の内容を取得します。 attr が空ならば要素内容を返す。'''
    elms = select(soup, selector)
    if attr:
        return [el[attr] if el.has_key(attr) else None for el in elms]
    else:
        return [el.text for el in elms]

