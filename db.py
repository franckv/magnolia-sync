import sqlite3

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

    def remove_all(self):
	self.remove_all_urls()
	self.remove_all_bookmarks()
	self.remove_all_tags()

    def remove_all_tags(self):
	cur = self.con.cursor()
	cur.execute('delete from moz_bookmarks where parent=4')

    def remove_all_urls(self):
	cur = self.con.cursor()
	cur.execute('delete from moz_places where id in (select fk from moz_bookmarks where type=1)')

    def remove_all_bookmarks(self):
	cur = self.con.cursor()
	cur.execute('delete from moz_bookmarks where type=1')

    def get_tags(self):
	all_tags = {}
	cur = self.con.cursor()
	cur.execute('select id, title from moz_bookmarks where type=2 and parent=4')
	for row in cur.fetchall():
	    self.tags[row[1]] = row[0]
	    all_tags[row[1]] = row[1]
	return all_tags

    def insert_tag(self, tag, now):
	cur = self.con.cursor()

	cur.execute('select id from moz_bookmarks where title=? and parent=4',
		(tag, ))
	row = cur.fetchone()
	if row != None:
	    self.tags[tag] = row[0]
	    return

	pos = self.get_current_tag_position() + 1
	# TODO: remove these magic numbers
	cur.execute('insert into moz_bookmarks (type, parent, position, title, dateAdded, lastModified) values (?, ?, ?, ?, ?, ?)',
		('2', '4', pos, tag, now, now))

	pos = self.insert_id()

	self.tags[tag] = pos

    def insert_url(self, url, title, rev_host):
	cur = self.con.cursor()

	cur.execute('select id from moz_places where url=?',
		(url, ))
	row = cur.fetchone()
	if row != None:
	    return row[0]

	cur.execute('insert into moz_places (url, title, rev_host) values (?, ?, ?)',
		(url, title, rev_host))

	return self.insert_id()

    def insert_bookmark(self, url_id, title, created, updated):
	cur = self.con.cursor()

	cur.execute('select id from moz_bookmarks where fk=? and parent=5', (url_id, ))
	row = cur.fetchone()
	if row != None:
	    return False

	pos = self.get_current_bookmark_position() + 1
	cur.execute('insert into moz_bookmarks (type, fk, parent, position, title, dateAdded, lastModified) values (?, ?, ?, ?, ?, ?, ?)',
		('1', url_id, '5', pos, title, created, updated))
	return True

    def insert_bookmark_toolbar(self, url_id, title, created, updated):
	cur = self.con.cursor()

	cur.execute('select id from moz_bookmarks where fk=? and parent=3', (url_id, ))
	row = cur.fetchone()
	if row != None:
	    return

	pos = self.get_current_bookmark_toolbar_position() + 1
	cur.execute('insert into moz_bookmarks (type, fk, parent, position, title, dateAdded, lastModified) values (?, ?, ?, ?, ?, ?, ?)',
		('1', url_id, '3', pos, title, created, updated))

    def insert_bookmark_tag(self, tag, url_id, title, created, updated):
	cur = self.con.cursor()

	tag_id = self.tags[tag]

	cur.execute('select id from moz_bookmarks where fk=? and parent=?',
		(url_id, tag_id))
	row = cur.fetchone()
	if row != None:
	    return

	pos = self.get_current_bookmark_tag_position(tag)
	cur.execute('insert into moz_bookmarks (type, fk, parent, position, title, dateAdded, lastModified) values (?, ?, ?, ?, ?, ?, ?)',
		('1', url_id, tag_id, pos, title, created, updated))

    # TODO: refactor to only 1 method
    def get_current_tag_position(self):
	cur = self.con.cursor()
	cur.execute('select max(position) from moz_bookmarks where type=2 and parent=4')
	row = cur.fetchone()
	cur.close()
	if row[0] == None:
	    return -1
	else:
	    return row[0]

    def get_current_bookmark_position(self):
	cur = self.con.cursor()
	cur.execute('select max(position) from moz_bookmarks where type=1 and parent=5')
	row = cur.fetchone()
	cur.close()
	if row[0] == None:
	    return -1
	else:
	    return row[0]

    def get_current_bookmark_toolbar_position(self):
	cur = self.con.cursor()
	cur.execute('select max(position) from moz_bookmarks where type=1 and parent=3')
	row = cur.fetchone()
	cur.close()
	if row[0] == None:
	    return -1
	else:
	    return row[0]

    def get_current_bookmark_tag_position(self, tag):
	cur = self.con.cursor()

	tag_id = self.tags[tag]

	cur.execute('select max(position) from moz_bookmarks where type=1 and parent=?',
		(tag_id, ))
	row = cur.fetchone()
	cur.close()
	if row[0] == None:
	    return -1
	else:
	    return row[0]

    def close(self):
	self.con.close()
