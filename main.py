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

    db.remove_all()

    now = time.time() * 1000000
    tags = pyg.tags_find(myself)
    for tag in tags:
        db.insert_tag(tag.name.lower(), now)

    time.sleep(1)

    bookmarks = pyg.bookmarks_find(person=myself)
    for bookmark in bookmarks:
	p = urlparse(bookmark.url)
	rev_host = p.hostname[::-1] + '.'
	url_id = db.insert_url(bookmark.url, bookmark.title, rev_host)
	created = str(get_timestamp(bookmark.created))
	updated = str(get_timestamp(bookmark.updated))
	db.insert_bookmark(url_id, bookmark.title, created, updated)
	tags = bookmark.tags
	for tag in tags:
	    db.insert_bookmark_tag(tag.lower(), url_id, bookmark.title, created, updated)
	    # ok this is just a personal convention
	    # TODO: make it more generic
	    if tag == 'toolbar':
		db.insert_bookmark_toolbar(url_id, bookmark.title, created, updated)

   
    db.commit()
    db.close()

if __name__ == '__main__':
    main()
