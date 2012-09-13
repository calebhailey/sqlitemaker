# stlib imports
import codecs
import csv
import datetime
import pdb
import uuid

# third-party imports
import sqlalchemy
from sqlalchemy import orm
#from sqlalchemy import ForeignKey
#from sqlalchemy import Sequence
#from sqlalchemy.orm import backref
#from sqlalchemy.orm import relation

# local imports
from Common import Logger
from CSV import CSV

class Database():
    def __init__(self, db_file=None, log_file=None, debug=False):
        self.dbms = 'unknown'
        self.metadata = sqlalchemy.MetaData()
        self.schema = {}
        self.tables = {}
        self.types = {}
        self.sources = {}
        self.logger = Logger(log_file, debug, 'Database.logger')
    
    def _detect_datatype(self, sample):
        """ Supported sqlalchemy types: Boolean, DateTime, Integer, Float, Text
        """
        #if not sample:
        #    #raise NotImplementedError('Expected a sample but got "%s"' % (sample))
        #    return sqlalchemy.types.String(convert_unicode=True)
        #if sample.title() in ['True', 'False']:
        #    return sqlalchemy.types.Boolean()
        #try:
        #    if int(sample):
        #        return sqlalchemy.types.Integer()
        #except ValueError:
        #    pass
        #try:
        #    if float(sample):
        #        return sqlalchemy.types.Float()
        #except ValueError:
        #    pass
        #for strf in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
        #    try:
        #        if datetime.datetime.strptime(sample, strf):
        #            return sqlalchemy.types.DateTime()
        #    except ValueError:
        #        pass
        return sqlalchemy.types.String(convert_unicode=True)
    
    def create_schema(self, table, column_names, samples):
        """ samples should be a generator yielding dicts from the csv (e.g. as 
            returned from DictReader()).
        """
        self.sources[table] = samples
        if not self.schema.has_key(table):
            self.schema[table] = []
        for column in column_names:
            index = column_names.index(column)
            sample = ''
            while True:
                try:
                    row = samples.next()
                    sample = row[column]
                    if sample != '':
                        break
                    if samples.line_num > 100:
                        break
                except StopIteration:
                    break
            if not sample:
                self.logger.log('could not find a sample for column: %s' % column, 'DEBUG')
            datatype = self._detect_datatype(sample)
            while True:
                if column.lower() in [name.lower() for name, value in self.schema[table]]:
                    self.logger.log('found duplicate column "%s"' % (column), 'INFO')
                    column += '_'
                else:
                    break
            self.schema[table].append((column, datatype))
            column_names[index] = column
        return column_names

    def create_table(self, table, primary_key):
        if not self.schema.get(table):
            raise RuntimeError('this database instance has no schema; please run create_schema first.')
        self.tables[table] = sqlalchemy.Table(table, self.metadata)
        for column, datatype in self.schema[table]:
            if column.lower() == primary_key.lower():
                self.tables[table].append_column(sqlalchemy.Column(column, datatype, primary_key=True))
            else:
                self.tables[table].append_column(sqlalchemy.Column(column, datatype))
        try:
            self.metadata.create_all(self.engine)
        except sqlalchemy.exceptions.OperationalError:
            self.logger.log('OperationalError while attempting to create database table!', 'ERROR')
            return
        class Type(object):
            def __init__(self):
                pass
        orm.mapper(Type, self.tables[table])
        self.types[table] = Type
        return self.types[table]
        
    def create_session(self):
        session = orm.sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()
        return self.session
        
    def commit(self, count=False):
        self.logger.log('starting to flush cache to %s database.' % (self.dbms), 'INFO')
        self.session.commit()
        self.logger.log('finished flushing cache to %s database.' % (self.dbms), 'INFO')
        if count:
            self.logger.log('total record count is %s.' % (count), 'INFO')
        return

class SQLite(Database):
    def __init__(self, db_file, log_file=None, debug=False):
        Database.__init__(self, log_file=log_file, debug=debug)
        self.dbms = 'sqlite'
        if not db_file:
            db_file = ':memory:'
            self.logger.log('using an in-memory SQLITE database!', 'DEBUG')
        self.file = 'sqlite:///' + db_file
        self.engine = sqlalchemy.create_engine(self.file)
        #self.metadata.reflect(bind=self.engine)
        self.create_session()

class DBCSV(CSV):
    """ Database.CSV adds primary key recommendation on top of the CSV.CSV base 
        class. 
    """
    def __init__(self, source, log_file=None, debug=False):
        CSV.__init__(self, source, log_file, debug)
    
    def read(self):
        """ A wrapper on csv.DictReader()
        """
        self.file = codecs.open(self.file.name, self.file.mode, self.file.encoding)
        self.data = csv.DictReader(self.file, dialect=self.dialect._name)
        if not self.recommendations:
            self._recommend()
        return self.data
    
    def _recommend(self):
        """ WUT? A recommendation engine to pick a column containing unique
            values to use as a primary key in a database? No way!
        """
        recommendations = {}
        for field in self.data.fieldnames:
            recommendations[field] = []
        while True:
            if self.data.line_num > 100:
                break
            try:
                document = self.data.next()
                for name, value in document.items():
                    if value in recommendations.get(name, [value]):
                        try:
                            recommendations.pop(name)
                        except KeyError:
                            continue
                    else:
                        recommendations[name].append(value)
            except UnicodeEncodeError:
                self.logger.log('UnicodeEncodeError on line #%s, using unicode-friendly fallback' % (self.data.line_num), 'DEBUG')
                document = self._get_row_by_line_num(self.data.line_num)
                for name, value in document.items():
                    if value in recommendations.get(name, [value]):
                        try:
                            recommendations.pop(name)
                        except KeyError:
                            continue
                    else:
                        recommendations[name].append(value)
            except StopIteration:
                break
        self.recommendations = recommendations.keys()
        return self.recommendations


if __name__ == '__main__':
    # self tests - sample data
    temp_csv = codecs.open('.temp.csv', 'wb', 'utf-8')
    temp_csv.write('"ID","First","Last"\n')
    temp_csv.write('"1","Bob","Jones"\n')
    temp_csv.write('"2","John","Doe"\n')
    temp_csv.write('"3","Jane","Fonda"\n')
    temp_csv.write('"4","Billy","Bob"\n')
    temp_csv.flush()
    temp_csv.close()

    # self tests - DBCSV
    test = DBCSV('.temp.csv')
    test.read()
    test.logger.debug = True
    test.logger.log('--', 'DEBUG')
    test.logger.log('created csv object instance from file "%s", with %s fields.' % (test.source, len(test.data.fieldnames)), 'DEBUG')
    
    # self tests - SQLite & Database
    sqlite = SQLite()
    sqlite.logger.debug = True
    sqlite.logger.log('created sqlite database instance file "%s"' % (sqlite.file), 'DEBUG')
    sqlite.logger.log('--', 'DEBUG')

