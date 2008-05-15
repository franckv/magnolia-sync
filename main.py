# -*- coding: utf-8 -*-

import os

import pygmalion
import pygmalion.Handlers
import pygmalion.Types
import pygmalion.Exceptions

from db import SQLConnector

import time
import datetime

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

    tags = pyg.tags_find(myself)
    for tag in tags:
        db.insert_tag(tag.name.lower())

    time.sleep(1)

    bookmarks = pyg.bookmarks_find(person=myself)
    for bookmark in bookmarks:
	url_id = db.insert_url(bookmark.url, bookmark.title)
	created = str(get_timestamp(bookmark.created))
	updated = str(get_timestamp(bookmark.updated))
	db.insert_bookmark(url_id, bookmark.title, created, updated)
	tags = bookmark.tags
	for tag in tags:
	    db.insert_bookmark_tag(tag.lower(), url_id, bookmark.title, created, updated)
   
    db.commit()
    db.close()



#Tags = pyg.tags_find(myself)
#
#For tag in tags:
#    print tag.name
#    print tag.count
#
#Time.sleep(1)

#bookmarks = pyg.bookmarks_find(person=myself,tags='anime')
#for bookmark in bookmarks:
#    print bookmark
#    created = time.strptime(bookmark.created, '%Y-%m-%dT%H:%M:%S-%Z:00')
#    print time(created)


#b = pyg.Bookmarks_Find(tags='emacs',person='inkedmn')
#c = pyg.Bookmarks_Update(id='voyenir',tags=['foo','bar','baz']) 
#d = pyg.Bookmarks_Delete(['vostigiba'])
#b = pyg.Bookmarks_Add('Test Bookmark','http://somecrap.com',
#	                      'description!','0',['foo','bar'],3)
#d = pyg.Bookmarks_Get(['hohogalath','whosestete'])
#
#r = pyg.Bookmarks_Tags_Add(['voyenir'],['bling','blong'])
#d = pyg.Bookmarks_Tags_Delete(['voyenir'],['foo'])
#
#p = pyg.Bookmarks_Tags_Replace(['voyenir'],'bar','bling')


#
#    alltags = api.tags_find(person=myself, tags='manga')
#	for tag in alltags:
#	    print tag
#	
#    bms = api.bookmarks_find(person=myself, tags='manga', limit='5')
#    print len(bms)
#    for bm in bms:
#      print bm.id
#      print ' ' + bm.title
#      print ' ' + bm.url
#      print ' ' + bm.description
#      print ' ' + bm.created[0:10]
#      print ' ' + bm.updated[0:10]
#      for tag  in bm.tags:
#	print ' >>' + tag
#      print
#


if __name__ == '__main__':
    main()
