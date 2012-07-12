#!/usr/bin/env python
#

""" A wrapper on the stlib csv module (and a few other things) to do useful 
    things with csv files.
"""

# stlib imports
import codecs
import csv
import os
import shutil
from exceptions import *


class CSV():
    """ Parse a CSV file and return a generator object that will spit out
        a python dict object representing a single row in the CSV file.  This is
        basically just a wrapper on csv.DictReader and csv.Sniffer.
    """
    def __init__(self, csv_file=None, *args, **settings):
        """ setup our instance.
        """
        self.default = {}
        self.default['quoting'] = csv.QUOTE_ALL
        self.default['delimiter'] = ','
        self.default['quotechar'] = '"'
        self.default['lineterminator'] = '\n'
        self.default['detected_dialect'] = False
        self.default['fieldnames'] = False
        for setting in settings:
            self.default[setting] = settings[setting]
        if csv_file:
            self.rename(csv_file)


    def rename(self, csv_file):
        """ Load the CSV file.
        """
        self.original_file_name = csv_file
        if os.path.exists(self.original_file_name):
            self.backup()


    def backup(self):
        """ Backup the original source file before we mung it up!
        """
        self.backup_file_name = self.original_file_name + '.bak'
        shutil.copy2(self.original_file_name, self.backup_file_name)


    def detect(self):
        """ A wrapper on csv.Sniffer().sniff()
        """
        f = open(self.backup_file_name, 'r')
        sample = f.readline()
        self.csv_format = csv.Sniffer().sniff(sample)
        csv.register_dialect(
            'detected_dialect',
            quotechar=self.csv_format.quotechar,
            delimiter=self.csv_format.delimiter,
            lineterminator=self.csv_format.lineterminator
            )
        self.default['detected_dialect'] = True
        f.close()


    def read(self):
        """ A wrapper on csv.DictReader()
        """
        self.detect()
        f = open(self.backup_file_name, 'r')

        f.seek(0)
        self.data = csv.DictReader(f, dialect='detected_dialect')
        for field in self.data.fieldnames:
            i = self.data.fieldnames.index(field)
            new_field = field.lstrip(codecs.BOM_UTF8)
            new_field = new_field.lstrip(codecs.BOM_UTF16)
            new_field = new_field.lstrip(codecs.BOM_UTF32)
            new_field = new_field.lstrip('"').rstrip('"')
            self.data.fieldnames[i] = new_field
        return self.data


    def bom_stripper(self):
        """ Strip the BOM from files before reading...
        """
        bom_file = open(self.original_file_name, 'rb')
        new_file = open(self.backup_file_name, 'wb')
        buffer = bom_file.read()
        buffer = buffer.lstrip(codecs.BOM_UTF8)
        buffer = buffer.lstrip(codecs.BOM_UTF16)
        buffer = buffer.lstrip(codecs.BOM_UTF32)
        new_file.write(buffer)
        new_file.flush()


    def writer(self, **settings):
        """ A wrapper on csv.DictWriter()
        """
        for setting in settings:
            self.default[setting] = settings[setting]
        if self.default['detected_dialect']: 
            self.dialect = 'detected_dialect'
        else:
            self.dialect = 'excel'
        if not self.data.fieldnames: 
            raise NotImplementedError
        self.f = open(self.original_file_name, 'w')
        self.output = csv.DictWriter(self.f, 
            self.data.fieldnames, 
            dialect=self.dialect, 
            quoting=self.default['quoting'],
            delimiter = self.default['delimiter'], 
            quotechar=self.default['quotechar'], 
            lineterminator=self.default['lineterminator']
            )


if __name__ == '__main__':
    pass


