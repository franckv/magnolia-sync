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

from xml.sax import ContentHandler

from Types import Bookmark, Tag, Response

class BookmarkListHandler(ContentHandler):
    def __init__(self):
        self.in_response = 0
        self.in_bookmarks = 0
        self.in_bookmark = 0
        self.in_title = 0
        self.in_url = 0
        self.in_description = 0
        self.in_screenshot = 0
        self.in_tags = 0

        self.bookmarklist = []
        self.temptags = []
        self.currentbm = Bookmark()

    def startElement(self, name, attrs):
        if name == 'bookmark':
            self.in_bookmark = 1
            self.currentbm.id = attrs.get('id', '').encode('utf-8')
            self.currentbm.created = attrs.get('created', '').encode('utf-8')
            self.currentbm.updated = attrs.get('updated', '').encode('utf-8')
            self.currentbm.rating = attrs.get('rating', '').encode('utf-8')
            if attrs.get('private', '') == 'false':
                self.private = False
            else:
                self.private = True
            self.currentbm.owner = attrs.get('owner', '').encode('utf-8')
        elif name == 'tag':
            self.temptags.append(attrs.get('name', '').encode('utf-8'))
        else:
            setattr(self, 'in_' + name, 1)


    def endElement(self, name):
        if name == 'bookmark':
            self.bookmarklist.append(self.currentbm)
            self.in_bookmark = 0
            self.currentbm = Bookmark()
            
        if name == 'tags':
            self.currentbm.tags = self.temptags
            self.temptags = []
        else:
            setattr(self, 'in_'+name, 0)

    def characters(self, content):
        if self.in_title:
            self.currentbm.title += content.encode('utf-8')
        elif self.in_url:
            self.currentbm.url += content.encode('utf-8')
        elif self.in_description:
            self.currentbm.description += content.encode('utf-8')
        elif self.in_screenshot:
            self.currentbm.screenshot_url += content.encode('utf-8')

class ShortBookmarkListHandler(ContentHandler):
    def __init__(self):
        self.bookmarklist = []
        self.in_bookmarks = 0
        self.in_bookmark = 0

    def startElement(self, name, attrs):
        if name == 'bookmarks':
            self.in_bookmarks = 1
        elif name == 'bookmark':
            b = Bookmark()
            b.ID = attrs.get('id', '').encode('utf-8')
            self.bookmarklist.append(b)

    def endElement(self, name):
        if name == 'bookmarks':
            self.in_bookmarks = 0

    def __str__(self):
        return '\n'.join([b.id for b in self.Bookmarks])


class TagListHandler(ContentHandler):
    def __init__(self):
        self.in_tags = 0
        self.tags = []
        
    def startElement(self, name, attrs):
        if name == 'tags':
            self.in_tags = 1
        elif name == 'tag':
            n = attrs.get('name', '').encode('utf-8')
            c = attrs.get('count', '').encode('utf-8')
            self.tags.append(Tag(n, c))

    def endElement(self, name):
        if name == 'tags':
            self.in_tags = 0

    def __str__(self):
        r = ''
        for t in self.tags:
            r += "%s : %s\n" % (t.name, t.count)
        return r

class EmptyResponseHandler(ContentHandler):
    def __init__(self):
        self.response = None

    def startElement(self, name, attrs):
        if name == 'response':
            self.response = Response(attrs.get('status', '').encode('utf-8'))

    def __str__(self):
        return "Status: %s" % self.response.status
