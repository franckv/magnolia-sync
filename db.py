import sqlite3
import time

from urlparse import urlparse

class SQLConnector():
    def __init__(self, db):
	self.con = None
	self.db = db
	self.tags = {}

    def connect(self):
	self.con = sqlite3.connect(self.db)

    def cursor(self):
	return self.con.cursor()

    def commit(self):
	self.con.commit()

    def insert_id(self):
	cur = self.con.cursor()
	cur.execute('SELECT LAST_INSERT_ROWID()')
	row = cur.fetchone()
	cur.close()
	return row[0]

    def insert_tag(self, tag):
	cur = self.con.cursor()

	cur.execute('select id from moz_bookmarks where title=? and parent=4', (tag, ))
	row = cur.fetchone()
	if row != None:
	    self.tags[tag] = row[0]
	    return

	pos = self.get_current_tag_position()
	date = time.time() * 1000000
	cur.execute('insert into moz_bookmarks (type, parent, position, title, dateAdded, lastModified) values (?, ?, ?, ?, ?, ?)', ('2', '4', pos, tag, date, date))

	pos = self.insert_id()

	self.tags[tag] = pos

    def insert_url(self, url, title):
	cur = self.con.cursor()

	cur.execute('select id from moz_places where url=?', (url, ))
	row = cur.fetchone()
	if row != None:
	    return row[0]

	p = urlparse(url)
	rev_host = p.hostname[::-1] + '.'

	cur.execute('insert into moz_places (url, title, rev_host) values (?, ?, ?)',
		(url, title, rev_host))

	return self.insert_id()

    def insert_bookmark(self, url_id, title, created, updated):
	cur = self.con.cursor()

	cur.execute('select id from moz_bookmarks where fk=? and parent=5', (url_id, ))
	row = cur.fetchone()
	if row != None:
	    return

	pos = self.get_current_bookmark_position()
	cur.execute('insert into moz_bookmarks (type, fk, parent, position, title, dateAdded, lastModified) values (?, ?, ?, ?, ?, ?, ?)',
		('1', url_id, '5', pos, title, created, updated))

    def insert_bookmark_tag(self, tag, url_id, title, created, updated):
	cur = self.con.cursor()

	tag_id = self.tags[tag]

	cur.execute('select id from moz_bookmarks where fk=? and parent=?', (url_id, tag_id))
	row = cur.fetchone()
	if row != None:
	    return


	pos = self.get_current_bookmark_tag_position(tag)
	cur.execute('insert into moz_bookmarks (type, fk, parent, position, title, dateAdded, lastModified) values (?, ?, ?, ?, ?, ?, ?)',
		('1', url_id, tag_id, pos, title, created, updated))

    def get_current_tag_position(self):
	cur = self.con.cursor()
	cur.execute('select max(position) from moz_bookmarks where type=2 and parent=4')
	row = cur.fetchone()
	cur.close()
	if row[0] == None:
	    return 0
	else:
	    return row[0]

    def get_current_bookmark_position(self):
	cur = self.con.cursor()
	cur.execute('select max(position) from moz_bookmarks where type=1 and parent=5')
	row = cur.fetchone()
	cur.close()
	if row[0] == None:
	    return 0
	else:
	    return row[0]

    def get_current_bookmark_tag_position(self, tag):
	cur = self.con.cursor()

	tag_id = self.tags[tag]

	cur.execute('select max(position) from moz_bookmarks where type=1 and parent=?', (tag_id, ))
	row = cur.fetchone()
	cur.close()
	if row[0] == None:
	    return 0
	else:
	    return row[0]

    def close(self):
	self.con.close()
