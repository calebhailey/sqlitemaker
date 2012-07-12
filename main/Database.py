#!/usr/bin/env python
#
# TODO: get serious about my docstrings...
#
#

""" A db management wrapper, using sqlalchemy...

"""

# imports
import datetime
from main.Text import Text
from sqlalchemy import Column
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
#from sqlalchemy import ForeignKey
#from sqlalchemy import Integer
#from sqlalchemy import Sequence
#from sqlalchemy.orm import backref
#from sqlalchemy.orm import relation

encoding = 'utf8'

class Database():
    """ A generic database class wrapping up the database platform independent \
    sweetness of sqlalchemy.  Use to inherit in backend-specific classes.
    
    """
    
    def __init__(self):
        """ Setup our instance...
        """
        self.metadata = MetaData()


    def createTable(self, table_name, fieldnames, primary_key):
        """ table_name = name of table as it will appear in the Database
            fieldnames = python list of fieldnames (as intended, this would come 
            from the csv.DictReader() "fieldnames" output).
        """
        schema, fieldnames = self.createSchema(fieldnames)  
        table = Table(table_name, self.metadata)
        for column in schema:
            field_type = schema[column]
            if column == primary_key:
                table.append_column(Column(column, field_type, primary_key=True))
            else:
                table.append_column(Column(column, field_type))
        self.metadata.create_all(self.engine)
        # create a new type to map to this table
        class objectModel(object):
            def __init__(self, **properties):
                for prop in properties:
                    setattr(self, prop, properties[prop])
        mapper(objectModel, table)
        # return fieldnames in case any renames take place, otherwise we'll
        # lose track of that column of data.
        return objectModel, fieldnames


    def createSchema(self, fieldnames, renames=False):
        """ Convert a python list of source file field names to a python dict \
            of key:String pairs for use with the createTable method.  
        
            NOTES: renames is a python dict of app:user fieldname pairs to use \
            to replace the user-named fields with application expected names.
        """
        def renamer(d,k):
            """ Check a dict (d) for a key (k) and rename the field if it
                already exists.
            """
            try:
                if d.has_key(k):
                    print datetime.datetime.now().isoformat(), 'WARNING: identified duplicate fieldname:', k
                    new_name = k + '_'
                    k = new_name
            except:
                pass
            return k
        schema = {}
        for field in fieldnames:
            key = fieldnames.index(field) # get the list item position
            field = renamer(schema,field.lower()) # rename (as needed)
            field = Text(field).unicode # unicode that badboy
            fieldnames[key] = field.lower() # update the list of fieldnames with the lower-cased, unicoded, and potentially renamed version 
            schema[field.lower()] = String(convert_unicode=True) # add the bitch to the schema dict
        # return fieldnames in case any renames take place, otherwise we'll
        # lose track of that column of data.
        return schema, fieldnames


    def createSession(self):
        """ Do stuff.
        """
        Session = sessionmaker()
        Session.configure(bind=self.engine)
        self.session = Session()
        return self.session


    def compareTable(self, table_name, fieldnames, primary_key=None):
        """ Compare fieldnames (columns) of data vs existing table to determine
            compatibility.
        """
        raise NotImplementedError


    def modifyTable(self, table_name, fieldnames, primary_key=None):
        """
        """
        raise NotImplementedError



class SQLite(Database):
    """ A class for creating SQLite databases...
    
    """
    def __init__(self, db_file=None):
        """ setup our instance.
            NOTES: db_file can either be a file path, or ':memory:' to create an 
            in-memory sqlite db.
        """
        Database.__init__(self)
        if db_file == None:
            db_file = ':memory:'
            print 'WARNING: using an in-memory SQLITE database!'
        self.db_location = 'sqlite:///' + db_file
        self.engine = create_engine(self.db_location)
        self.metadata.reflect(bind=self.engine)
        self.tables = self.engine.table_names()


if __name__ == '__main__':
    pass


