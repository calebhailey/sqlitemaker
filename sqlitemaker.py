#!/usr/bin/env python
#

# stlib imports
import pdb
import sys

# local imports
from main.Common import Logger, Settings
from main.Database import DBCSV, SQLite
from main.Options import Options


class SQLiteMaker(object):
    def __init__(self):
        self.logger = Logger()
        self.config = Settings('settings.json') 

        #
        # command line interface stuff...
        #
        self.option = Options(prog='sqlitemaker')

        # option groups
        self.option.addGroup(
            'Input Options', 
            'Input options description...'
        )
        self.option.addGroup(
            'Output Options', 
            'Output options description...'
        )

        # options
        self.option.addOption(
            'Input Options', 
            '-i --input', 
            'input', 
            metavar='CSV FILE',
            #required=True,
            help='Absolute or relative path to input %(metavar)s.'
        )
        self.option.addOption(
            'Input Options', 
            '-p --primary_key', 
            'primary_key', 
            metavar='PRIMARY KEY',
            default=None,
            help='Column name from source csv to use as the datbase %(metavar)s.'
        )
        self.option.addOption(
            'Output Options', 
            '-o --output', 
            'output', 
            metavar='SQLITE DB FILE',
            help='Absolute or relative path to output %(metavar)s. Defaults to <input file name>.db'
        )
        self.option.addOption(
            'Output Options', 
            '-t --table', 
            'table', 
            default='records', 
            metavar='TABLE',
            help='Name to use for new SQL DB %(metavar)s. Defaults to "%(default)s".' 
        )

        # parse those bad boys
        self.option.parseArgs() # availble at self.option.arguments

    def recommend(self):
        recommended = None
        print('\n\tPlease select a primary key from one of the following:\n')
        for field in sorted(self.csv.recommendations):
            index = sorted(self.csv.recommendations).index(field)
            if not recommended and 'id' in field.lower():
                recommended = field
                field += ' (recommended)'
            print('\t\t%s. %s' % (index, field))
        selection = raw_input('\n\tSelect one: ')
        print()
        if not selection:
            selection = recommended
        try:
            index = [i.lower() for i in sorted(self.csv.recommendations)].index(selection.lower())
            primary_key = sorted(self.csv.recommendations)[index]
        except ValueError:
            primary_key = sorted(self.csv.recommendations)[int(selection)]
        return primary_key        

    def setup_database(self, db_file, table, primary_key):
        self.db = SQLite(db_file)
        #db.logger.debug = True
        self.csv.data.fieldnames = self.db.create_schema(table, self.csv.data.fieldnames, self.csv.data)
        self.db.create_table(table, primary_key)
        self.db.commit()
        return self.csv, self.db

    def process(self):
        self.csv.read() # reset csv.data
        count = 0
        while True:
            try:
                row = self.csv.data.next()
                count +=1
            except UnicodeEncodeError:
                self.csv.logger.log('UnicodeEncodeError on line #%s, using unicode-friendly fallback' % (self.csv.data.line_num), 'DEBUG')
                row = self.csv._get_row_by_line_num(self.csv.data.line_num)
                count +=1
            except StopIteration:
                break
            except:
                self.csv.logger.log('something still went wrong on line #%s' % (self.csv.data.line_num), 'ERROR')
            record = self.db.types[self.table]()
            for field in row:
                record.__dict__[field] = row[field]
            self.db.session.add(record)
            if self.config.settings.pages:
                if count % self.config.settings.pages == 0:
                    self.db.commit(count)
        self.db.commit(count)
        return

    def run(self, input_file, table, primary_key, output_file):
        self.csv = DBCSV(input_file)
        self.csv.read()
        self.table = table
        self.primary_key = primary_key
        if not self.table:
            self.table = 'records'
        if not self.primary_key:
            self.primary_key = self.recommend()
        if not output_file:
            output_file = input_file + '.sqlite'
        self.csv, self.db = self.setup_database(output_file, self.table, self.primary_key)
        self.process()

if __name__ == '__main__':
    sqlitemaker = SQLiteMaker()

    # debug output
    sqlitemaker.logger.debug = True
    sqlitemaker.logger.log('--', 'DEBUG')
    sqlitemaker.logger.log('config file settings: %s' % sqlitemaker.config.settings, 'DEBUG')
    sqlitemaker.logger.log('arguments: %s' % (sqlitemaker.option.arguments.__dict__), 'DEBUG')
    sqlitemaker.logger.log('python version: %s' % (sys.version.replace('\n', '')), 'DEBUG')
    sqlitemaker.logger.log('--', 'DEBUG')
    
    # do stuff
    if sqlitemaker.option.arguments.input:
        sqlitemaker.run(
            sqlitemaker.option.arguments.input,
            sqlitemaker.option.arguments.table,
            sqlitemaker.option.arguments.primary_key,
            sqlitemaker.option.arguments.output
        )


