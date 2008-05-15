import Handlers

class Response(object):
    """Describes a response object from an empty response from magnolia"""
    def __init__(self, status):
        self.status = status

class Tag(object):
    """Describes a tag from a tag list response from magnolia"""
    def __init__(self, name, count=0):
        self.name = name
        self.count = count

    def __str__(self):
        return "%s: %s" % (self.name, self.count)

class Bookmark(object):
    """Describes a Ma.gnolia.com bookmark object,
    specifically for storing parsed data from API calls"""

    def __init__(self, id='', created='', updated='', rating='0',
                 private=False, owner='', title='', url='',
                 desc='', screen='', tags=[]):
        self.id = id
        self.created = created
        self.updated = updated
        self.rating = rating
        self.private = private
        self.owner = owner
        self.title = title
        self.url = url
        self.description = desc
        self.screenshot_url = screen
        self.tags = tags

    def __str__(self):
        s = """
Bookmark:
\tID: %s
\tCreated: %s
\tUpdated: %s
\tRating: %s
\tPrivate: %s
\tOwner: %s
\tTitle: %s
\tURL: %s
\tDesc: %s
\tScreen: %s
\tTags: %s
        """ % (self.id.encode('utf-8'), self.created, self.updated, self.rating, self.private,
               self.owner, self.title, self.url, self.description, self.screenshot_url,
               ','.join(self.tags))
        return s.strip()

    def __repr__(self):
        return "<%s: %s (%s)>" % (self.__class__.__name__,
                                  self.title,
                                  self.url)

