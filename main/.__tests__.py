# stlib imports
import codecs
import datetime
import pdb

# local imports
from Database import DBCSV, SQLite

def init_database(table, csv, primary_key):
    db_file = csv.source + '.db'
    db = SQLite(db_file)
    #db.logger.debug = True
    csv.data.fieldnames = db.create_schema(table, csv.data.fieldnames, csv.data)
    db.create_table(table, primary_key)
    db.commit()
    return csv, db

def process_csv(csv, db, table, primary_key, pages=None):
    csv.read() # reset csv.data
    count = 0
    while True:
        try:
            row = csv.data.next()
            count +=1
        except UnicodeEncodeError:
            csv.logger.log('UnicodeEncodeError on line #%s, using unicode-friendly fallback' % (csv.data.line_num), 'DEBUG')
            row = csv._get_row_by_line_num(csv.data.line_num)
            count +=1
        except StopIteration:
            break
        except:
            csv.logger.log('something still went wrong on line #%s' % (csv.data.line_num), 'ERROR')
        record = db.types[table]()
        for field in row:
            record.__dict__[field] = row[field]
        db.session.add(record)
        if pages:
            if count % pages == 0:
                db.commit(count)
    db.commit(count)
    return

def run(csv_file, table):
    csv = DBCSV(csv_file)
    csv.logger.debug = True
    csv.read()
    # pick one of the recommended primary key fields!
    recommended = None
    print('\nPlease select a primary key from one of the following:\n')
    for field in sorted(csv.recommendations):
        index = sorted(csv.recommendations).index(field)
        if not recommended and 'id' in field.lower():
            recommended = field
            field += ' (recommended)'
        print('\t%s. %s' % (index, field))
    selection = raw_input('\nSelect one: ')
    print()
    if not selection:
        selection = recommended
    try:
        index = [i.lower() for i in sorted(csv.recommendations)].index(selection.lower())
        primary_key = sorted(csv.recommendations)[index]
    except ValueError:
        primary_key = sorted(csv.recommendations)[int(selection)]
    csv, db = init_database(table, csv, primary_key)
    process_csv(csv, db, table, primary_key, 10000)
    return csv, db

if __name__ == '__main__':
    csv_file = '5016d4fe7653517083000446-simple.csv'
    #csv_file = 'sample.csv'
    table = 'test'
    run(csv_file, table)

