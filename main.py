# -*- coding: utf-8 -*-

import os

import pygmalion
import pygmalion.Handlers
import pygmalion.Types
import pygmalion.Exceptions

from db import SQLConnector

import time
import datetime
from urlparse import urlparse

key_file = open('key', 'r')
api_key = key_file.readline().rstrip()
key_file.close()

myself = 'franck_v'

def get_timestamp(date):
    yyyy = int(date[0:4])
    mm = int(date[5:7])
    dd = int(date[8:10])
    HH = int(date[11:13])
    MM = int(date[14:16])
    SS = int(date[17:19])
    op = date[19]
    tz = int(date[20:22])

    offset = tz * 60
    if op == '-':
	offset = -offset

    dateutc = datetime.datetime(yyyy, mm, dd, HH, MM, SS) + datetime.timedelta(minutes=offset)

    return int(1000000*time.mktime(dateutc.timetuple()))

def main():
    pyg = pygmalion.Pygmalion(api_key)

    db = SQLConnector('/home/franck/places.sqlite')
    db.connect()

    now = time.time() * 1000000
    tags = pyg.tags_find(myself)
    print 'found %i tags' % len(tags)
    old_tags = db.get_tags()
    print 'comparing with %i old tags' % len(old_tags)

    added = 0
    unchanged = 0
    deleted = 0

    new_tags = {}
    for tag in tags:
	if old_tags.has_key(tag.name.lower()):
	    unchanged += 1
	    del old_tags[tag.name.lower()]
	else:
	    added += 1
	    new_tags[tag.name.lower()] = tag.name.lower()

    for tag in old_tags:
	deleted += 1

    print '%i added, %i unchanged, %i deleted' % (added, unchanged, deleted)

    #db.remove_all()
    for tag in new_tags:
        db.insert_tag(tag, now)

    time.sleep(1)

    date = None
    done = False
    while (not done):
	if date != None:
	    bookmarks = pyg.bookmarks_find(person=myself, to=date)
	else:
	    bookmarks = pyg.bookmarks_find(person=myself)

	if len(bookmarks) < 500:
	    done = True

	print 'found %i bookmarks' % len(bookmarks)
	added = 0
	unchanged = 0
	for bookmark in bookmarks:
	    p = urlparse(bookmark.url)
	    rev_host = p.hostname[::-1] + '.'
	    url_id = db.insert_url(bookmark.url, bookmark.title, rev_host)
	    created = str(get_timestamp(bookmark.created))
	    updated = str(get_timestamp(bookmark.updated))
	    date = bookmark.created
	    if db.insert_bookmark(url_id, bookmark.title, created, updated):
		added += 1
	    else:
		unchanged += 1

	    tags = bookmark.tags
	    for tag in tags:
		db.insert_bookmark_tag(tag.lower(), url_id, bookmark.title, created, updated)
		# ok this is just a personal convention
		# TODO: make it more generic
		if tag == 'toolbar':
		    db.insert_bookmark_toolbar(url_id, bookmark.title, created, updated)
	time.sleep(1)
    
    print '%i added, %i updated' % (added, unchanged)
   
    db.commit()
    db.close()

if __name__ == '__main__':
    main()
