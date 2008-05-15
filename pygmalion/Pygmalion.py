#!/usr/bin/env python

# Copyright (c) 2006 Brett Kelly
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Portions of the included source code are copyright by its original author(s)
# and remain subject to its associated license.


import httplib
import urllib

import xml.sax

import Handlers
import Types
import Exceptions

__author__ = 'Brett Kelly'
__email__ = 'inkedmn@gmail.com'
__version__ = '0.1'
__desc__ = 'Python implementation of Ma.gnolia.com Web API'
__apiVersion__ = '1'

debug = False

def _execApiCall(headers, params, method_name,
                domain='ma.gnolia.com',
                urlhead='/api/rest/1/'):
    """ Generic function to make a call to the magnolia API and return
    the response object.

    Params need to be encoded properly w/ urllib.urlencode()
    """
    
    if 'api_key' not in params and method_name not in ['echo', 'get_key']:
        raise MagnoliaException('Required API Key parameter missing')
    conn = httplib.HTTPConnection(domain)
    conn.request('POST', urlhead + method_name, params, headers)
    return conn.getresponse()


###
# API Method Wrappers
###

class Pygmalion(object):
    """Class for user to interface with library - wraps available API
    methods"""

    def __init__(self, api_key):
        self.apikey = api_key
        self.headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'Accept': 'text/plain' }
        
    def bookmarks_get(self, bookmarkids):
        """Get bookmarks by their internal ma.gnolia ID"""
        assert type(bookmarkids) == list
        if not len(bookmarkids):
            raise Exception("At least one bookmark ID is required")
        methname = 'bookmarks_get'
        handler = Handlers.BookmarkListHandler()
        params = urllib.urlencode(
            { 'api_key': self.apikey,
              'id': ','.join(bookmarkids) })
        response = _execApiCall(self.headers, params, methname)
        xmltxt = response.read()
        xml.sax.parseString(xmltxt, handler)
        return handler.bookmarklist

    def bookmarks_find(self, **kwargs):
        """Find bookmarks based on search parameters in kwargs"""
        if not len(kwargs):
            raise Exception("Please supply at least one search parameter")
        methname = 'bookmarks_find'
        handler = Handlers.BookmarkListHandler()
        regparams = {}
        regparams['api_key'] = self.apikey
        for k,v in kwargs.iteritems():
            regparams[k] = v
        encparams = urllib.urlencode(regparams)
        response = _execApiCall(self.headers, encparams, methname)
        xmltxt = response.read()
        xml.sax.parseString(xmltxt,handler)
        return handler.bookmarklist

    def bookmarks_delete(self, bookmarkids):
        assert type(bookmarkids) == list
        if not len(bookmarkids):
            raise Exception("At least one bookmark ID is required")
        methname = 'bookmarks_delete'
        handler = Handlers.ShortBookmarkListHandler()
        params = urllib.urlencode(
            { 'api_key': self.apikey,
              'id': ','.join(bookmarkids) }) 
        response = _execApiCall(self.headers, params, methname)
        xmltxt = response.read()
        xml.sax.parseString(xmltxt, handler)
        return handler.bookmarklist

    def bookmarks_add(self, title, url, description='', private='0', tags=[], rating='0'):
        methname = 'bookmarks_add'
        handler = Handlers.BookmarkListHandler()
        params = urllib.urlencode(
            { 'api_key': self.apikey,
              'title': title,
              'url': url,
              'description': description,
              'private': private,
              'tags': ','.join(tags),
              'rating': rating } )
        response = _execApiCall(self.headers, params, methname)
        xmltxt = response.read()
        xml.sax.parseString(xmltxt, handler)
        return handler.bookmarklist

    def bookmarks_update(self, id, **kwargs):
        methname = 'bookmarks_update'
        handler = Handlers.BookmarkListHandler()
        rawparams = {}
        rawparams['api_key'] = self.apikey
        rawparams['id'] = id
        for k,v in kwargs.iteritems():
            if k == 'tags':
                rawparams[k] = ','.join(v)
            else:
                rawparams[k] = v
        encparams = urllib.urlencode(rawparams)
        response = _execApiCall(self.headers, encparams, methname)
        xmltxt = response.read()
        xml.sax.parseString(xmltxt, handler)
        return handler.bookmarklist

    def bookmarks_tags_add(self, ids, tags):
        methname = 'bookmarks_tags_add'
        handler = Handlers.EmptyResponseHandler()
        params = urllib.urlencode(
            { 'api_key': self.apikey,
              'id': ','.join(ids),
              'tags': ','.join(tags) })
        response = _execApiCall(self.headers, params, methname)
        xmltxt = response.read()
        xml.sax.parseString(xmltxt, handler)
        return handler.Response

    def bookmarks_tags_delete(self, ids, tags):
        methname = 'bookmarks_tags_delete'
        handler = Handlers.EmptyResponseHandler()
        params = urllib.urlencode(
            { 'api_key': self.apikey,
              'id': ','.join(ids),
              'tags': ','.join(tags) })
        response = _execApiCall(self.headers, params, methname)
        xmltxt = response.read()
        xml.sax.parseString(xmltxt, handler)
        return handler.Response

    def bookmarks_tags_replace(self, ids, oldtag, newtag):
        methname = 'bookmarks_tags_replace'
        handler = Handlers.EmptyResponseHandler()
        params = urllib.urlencode(
            { 'api_key': self.apikey,
              'id': ','.join(ids),
              'old': oldtag,
              'new': newtag })
        response = _execApiCall(self.headers, params, methname)
        xmltxt = response.read()
        xml.sax.parseString(xmltxt, handler)
        return handler.Response

    def tags_find(self,user):
        methname = 'tags_find'
        handler = Handlers.TagListHandler()
        params = urllib.urlencode(
            { 'api_key': self.apikey,
              'person': user })
        response = _execApiCall(self.headers, params, methname)
        xmltxt = response.read()
        xml.sax.parseString(xmltxt, handler)
        return handler.tags
    
