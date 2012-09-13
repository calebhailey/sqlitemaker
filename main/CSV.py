# stlib imports
import codecs
import csv
import os
import shutil

# local imports
from Common import Logger

# naughty globals
encoding = 'utf-8-sig'

class CSV(object):
    def __init__(self, source, log_file=None, debug=False):
        self.source = source
        self.file = codecs.open(self.source, 'rb', encoding)
        self.dialect = csv.excel # default dialect
        self.backup()
        self.sniff()
        self.recommendations = []
        self.logger = Logger(log_file, debug, 'CSV.logger')

    def backup(self):
        backup = self.source + '.bak'
        if not os.path.exists(backup):
            shutil.copy2(self.source, backup)

    def sniff(self):
        """ A wrapper on csv.Sniffer().sniff()
        """
        self.file = codecs.open(self.file.name, self.file.mode, self.file.encoding)
        sample = self.file.readline()
        self.dialect = csv.Sniffer().sniff(sample)
        for name, value in self.dialect.__dict__.items():
            if isinstance(value, unicode):
                self.dialect.__dict__[name] = str(value)
        csv.register_dialect(self.dialect._name, self.dialect) # self.dialect._name = 'sniffed'
        return self.dialect

    def read(self):
        """ A wrapper on csv.DictReader()
        """
        self.file = codecs.open(self.file.name, self.file.mode, self.file.encoding)
        self.data = csv.DictReader(self.file, dialect=self.dialect._name)
        return self.data

    def _get_row_by_line_num(self, line_num):
        csv = codecs.open(self.file.name, self.file.mode, self.file.encoding)
        count = 0
        while True:
            line = csv.readline()
            count += 1
            if count == line_num + 1:
                break
        delimiter = '%s%s%s' % (self.dialect.quotechar, self.dialect.delimiter, self.dialect.quotechar)
        line = line.lstrip(self.dialect.quotechar).rstrip(self.dialect.quotechar)
        line = line.split(delimiter)
        line_dict = {}
        for field in self.data.fieldnames:
            index = self.data.fieldnames.index(field)
            line_dict[field] = line[index]
        return line_dict

if __name__ == '__main__':
    # self tests
    temp_csv = codecs.open('.temp.csv', 'wb', 'utf-8')
    temp_csv.write('"ID","First","Last"\n')
    temp_csv.write('"1","Bob","Jones"\n')
    temp_csv.write('"2","John","Doe"\n')
    temp_csv.write('"3","Jane","Fonda"\n')
    temp_csv.write('"4","Billy","Bob"\n')
    temp_csv.flush()
    temp_csv.close()
    test = CSV('.temp.csv')
    test.read()
    test.logger.debug = True
    test.logger.log('created csv object instance from file "%s", with %s fields.' % (test.source, len(test.data.fieldnames)), 'DEBUG')


