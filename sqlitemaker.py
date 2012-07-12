#!/usr/bin/env python
#

""" Convert a properly structured csv file to a SQLite database.

    Usage example:
    
    python sqlitemaker.py -i sampledata.csv -o sampledata.sqlite
    
"""

# imports
import datetime
import sys
import uuid
from main.Configuration import Configuration
from main.Options import Options
from main.CSV import CSV
from main.Database import SQLite
from main.Text import Text

class SQLiteMaker():
    """ Documentation!
    """
    def __init__(self, csv=False, db=False):
        """ Configure our instance and get ready to make magic happen.
        """


    def interface(self):
        """ Command line options and help documentation.
        """
        # read config file & command line arguments
        self.config = Configuration('.sqlitemaker', 'settings.ini')
        self.config.readSettingsFiles()
        self.options = Options('sqlitemaker')
        self.parser = self.options.parser

        # option groups
        self.options.addGroup(
            'CSV INPUT',
            '<...description...>'
            )
        self.options.addGroup(
            'SQLITE OUTPUT',
            '<...description...>'
            )

        # options
        self.options.addOption(
            'CSV INPUT',
            '-i --input',
            'csv_input',
            metavar='CSV_FILE',
            default=False,
            help='Provide a %(metavar)s to use for the %(dest)s option...'
            )
        self.options.addOption(
            'SQLITE OUTPUT',
            '-o --output',
            'db_sqlite_file',
            metavar='SQLITE_DB_FILE',
            default=False,
            help='Provide a %(metavar)s to use for the %(dest)s option...'
            )
        self.options.addOption(
            'SQLITE OUTPUT',
            '-t --table',
            'db_table_name',
            metavar='TABLE_NAME',
            default='',
            help='Provide a %(metavar)s to use for the %(dest)s option...'
            )
        self.options.addOption(
            'SQLITE OUTPUT',
            '-p --primarykey',
            'db_primary_key',
            metavar='COLUMN_NAME',
            default='',
            help='Provide a %(metavar)s to use for the %(dest)s option...'
            )
        self.arguments = self.options.parseArgs().__dict__
        return self.config, self.arguments


    def load_csv(self, csv, check_field=False):
        self.csv = CSV(csv)
        self.csv.read()
        if check_field:
            self.check_field(check_field)


    def check_field(self, field):
        """check for specific field, add it if it's missing
        """
        try:
            self.csv.data.fieldnames.index(field)
        except ValueError:
            self.csv.data.fieldnames.append(field)


    def init_db(self, db, table_name=False, fieldnames=False, pk=False):
        self.db = SQLite(db)
        if table_name:
            if fieldnames:
                if pk:
                    self.create_table_and_map_object(table_name, fieldnames, pk)
        else:
            return self.db
        self.session = self.db.createSession()


    def create_table_and_map_object(self, name, fieldnames, pk):
        self.object, self.csv.data.fieldnames = self.db.createTable(name, fieldnames, pk)
        return self.object, self.csv.data.fieldnames
        

    def commit(self, count=False):
        print datetime.datetime.now().isoformat(), 'INFO: starting to flush record cache to sqlite3 db...'
        self.session.commit()
        print datetime.datetime.now().isoformat(), 'INFO: finished flushing record cache to sqlite3 db...'
        if count:
            print datetime.datetime.now().isoformat(), 'INFO: total record count is', count


    def parse_csv(self, pk, pages=False):
        rows, count = True, 0
        while rows:
            try:
                row = self.csv.data.next()
                count += 1
            except StopIteration:
                break
            except:
                print '\n', datetime.datetime.now().isoformat(), 'ERROR: failed to process doc #', count, '?\n'
                continue
            record = self.object()
            if not row[pk]:
                row[pk] = str( uuid.uuid4() )
            for i in row:
                row[i] = Text(row[i]).unicode
                record.__dict__[i] = row[i]
            self.session.add(record) # lazy add (in memory only)
            if pages:
                if not count % pages:
                    # for paged flush to disk
                    self.commit(count)
        # flush all in-memory objects to disk
        self.commit(count)


if __name__ == "__main__":
    sm = SQLiteMaker()
    config, arguments = sm.interface()
    # print datetime.datetime.now().isoformat(), 'INFO: executing this script with the following options:\n\n\t', 
    # for i in sys.argv: print i,
    # print '\n'
    if len(sys.argv) < 2:
        sm.parser.print_help()
    elif arguments['csv_input']:
        if not arguments['db_sqlite_file']: arguments['db_sqlite_file'] = arguments['csv_input'] + '.sqlite'
        if not arguments['db_table_name']: arguments['db_table_name'] = 'sqlitemaker'
        if not arguments['db_primary_key']: arguments['db_primary_key'] = 'sqlitemaker_id'
        sm.load_csv(
            arguments['csv_input'],
            arguments['db_primary_key']
        )
        sm.init_db(
            arguments['db_sqlite_file'],
            arguments['db_table_name'],
            sm.csv.data.fieldnames,
            arguments['db_primary_key']
        )
        sm.parse_csv(arguments['db_primary_key'], pages=10000)

