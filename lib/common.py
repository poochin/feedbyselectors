#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import django
from google.appengine.api.users import User
from google.appengine.ext.webapp import template
from django.utils import feedgenerator

import models
from soupselect import select

def error(handler, no, message="Fail to load."):
    '''error(handler, no, message="Fail to load.")

    RequestHandler を使いエラーを出力します
    '''
    handler.error(no)
    path = os.path.join(os.path.dirname(__file__), '../templates/error.html')
    handler.response.out.write(template.render(path, {'error_message': message}))


def currentuser():
    '''currentuser()
    
    ログイン中のユーザエンティティを返します
    '''
    user = User()
    u = models.User.all().('user =', user).get()
    if not u:
        u = models.User(user=user)
        u.put()
        if not u.is_saved():
            return None
    return u


def selectortext(soup, selector, attr):
    '''selectortext(soup, selector, attr)

    soup オブジェクトについて selector でオブジェクトを指定し、
    その soup オブジェクトの attr 属性の値を取得します。
    ただし attr == None の場合は要素内容を返します。
    '''
    elms = select(soup, selector)
    if attr:
        return [el[attr] if el.has_key(attr) else None for el in elms]
    else:
        return [el.text for el in elms]


def buildatom(author, rss_title, rss_link, rss_description, items):
    '''buildatom(author, rss_title, rss_link, rss_description, items)

    django の feedgenerator を使用して Atom を作成します
    '''
    fg = feedgenerator.Atom1Feed(
        title=rss_title,
        link=rss_link,
        description=rss_description,
        language=u'ja',
        author_name=author)

    for item in items:
        fg.add_item(**item)

    return fg.writeString('UTF-8')


def buildrss(author, rss_title, rss_link, rss_description, items):
    '''buildrss(author, rss_title, rss_link, rss_description, items)

    django の feedgenerator を使用して RSS を作成します
    '''
    fg = feedgenerator.Rss201rev2Feed(
        title=rss_title,
        link=rss_link,
        description=rss_description,
        language=u'ja',
        author_name=author)

    for item in items:
        fg.add_item(**item)

    return fg.writeString('UTF-8')

def buildrdf(author, rss_title, rss_link, rss_description, items):
    '''buildrdf(author, rss_title, rss_link, rss_description, items)

    django の feedgenerator を使用して RDF を作成します
    '''
    fg = feedgenerator.RssUserland091Feed(
        title=rss_title,
        link=rss_link,
        description=rss_description,
        language=u'ja',
        author_name=author)

    for item in items:
        fg.add_item(**item)

    return fg.writeString('UTF-8')

