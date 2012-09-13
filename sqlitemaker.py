#!/usr/bin/env python
#

# stlib imports
import os
import pdb
import sys

# local imports
from main.Common import Logger, Settings
from main.Database import DBCSV, SQLite
from main.Options import Options

class SQLiteMaker(object):
    def __init__(self, settings_file, log_file=None, debug=False):
        self.logger = Logger(log_file, debug, source='sqlitemaker.logger')
        self.config = Settings(settings_file, log_file=log_file, debug=debug)

        #
        # command line interface stuff...
        #
        self.option = Options(prog='sqlitemaker', log_file=self.logger.log_file, debug=self.logger.debug)

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
        if len(self.csv.recommendations) == 1:
            primary_key = self.csv.recommendations[0]
            self.csv.logger.log('automatically selecting the "%s" field as the primary_key (it is the only field containing unique contents)' % (primary_key), 'DEBUG')
            return primary_key
        recommended = None
        print('\n\tPlease select a primary key from one of the following:\n')
        for field in sorted(self.csv.recommendations):
            index = sorted(self.csv.recommendations).index(field)
            if not recommended and 'id' in field.lower():
                recommended = field
                field += ' (recommended)'
            print('\t\t%s. %s' % (index, field))
        selection = raw_input('\n\tSelect one: ')
        print('')
        if not selection:
            selection = recommended
        try:
            index = [i.lower() for i in sorted(self.csv.recommendations)].index(selection.lower())
            primary_key = sorted(self.csv.recommendations)[index]
        except ValueError:
            primary_key = sorted(self.csv.recommendations)[int(selection)]
        return primary_key        

    def setup_database(self, db_file, table, primary_key):
        self.db = SQLite(db_file, log_file=self.logger.log_file, debug=self.logger.debug)
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
        self.csv = DBCSV(input_file, log_file=self.logger.log_file, debug=self.logger.debug)
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
    working_dir = os.path.dirname(os.path.abspath(__file__))
    settings_file = os.path.join(working_dir, 'settings.json')
    log_file = 'sqlitemaker.log' #write output to current directory vs installed path
    #sqlitemaker = SQLiteMaker(settings_file, log_file, debug=True)
    #sqlitemaker = SQLiteMaker(settings_file, debug=True)
    sqlitemaker = SQLiteMaker(settings_file, log_file)
    
    if sqlitemaker.option.arguments.input:
        sqlitemaker.run(
            sqlitemaker.option.arguments.input,
            sqlitemaker.option.arguments.table,
            sqlitemaker.option.arguments.primary_key,
            sqlitemaker.option.arguments.output
        )


