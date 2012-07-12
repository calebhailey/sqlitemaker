#!/usr/bin/env python
#

# stlib imports


class Text():
    """ A generic text class (which is mostly a wrapper on stdlib modules) to do 
        stuff with text.
    """
    def __init__(self, text=None):
        """ Setup our instance...
        """
        self.encoding = 'utf-8'
        self.unicode = u''
        if not text == None:
            self.unicoder(text)


    def unicoder(self, text):
        if isinstance(text, basestring):
            if not isinstance(text, unicode):
                self.unicode = unicode(text, self.encoding)
            else:
                self.unicode = text
        return self.unicode


if __name__ == '__main__':
    pass

