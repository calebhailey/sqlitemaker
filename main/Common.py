# stlib imports
import codecs
import datetime
import json
import os
import pdb
import sys

# naughty globals
encoding = 'utf-8'

class dotdict(dict):
    def __getattr__(self, attr):
        return self.get(attr, None)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

class Settings(object):
    def __init__(self, settings_file, section=None, log_file=None, debug=False):
        self.logger = Logger(log_file, debug, 'Settings.logger')
        self.source = settings_file
        if os.path.exists(self.source):
            self.file = codecs.open(self.source, 'rb', encoding)
            self.settings = dotdict(self.read(section))
            self.file.close()
        else:
            self.settings = dotdict({})
            self.logger.log('unable to locate file %s' % (os.path.abspath(settings_file)), 'ERROR')

    def read(self, section):
        self.file = codecs.open(self.file.name, self.file.mode, self.file.encoding)
        self.settings = json.loads(self.file.read())
        self.file.close()
        if section:
            return self.settings[section]
        else:
            return self.settings

class Logger(object):
    def __init__(self, log_file=None, debug=False, source=None):
        self.source = source
        if isinstance(log_file, (codecs.StreamWriter, codecs.StreamReaderWriter)):
            self.log_file = log_file
        elif isinstance(log_file, str):
                self.log_file = codecs.open(log_file, 'ab', 'utf-8')
        else:
            self.log_file = sys.stdout
        #if os.path.exists(self.log_file.name):
        #    filename, extension = os.path.splitext(self.log_file.name)
        #    timestamp = datetime.datetime.now().isoformat()
        #    self.log_file = codecs.open('%s_%s%s' % (filename, timestamp, extension), self.log_file.mode, self.log_file.encoding)
        self.debug = debug
        if source:
            self.log('initializing logging for module: %s' % (source), 'DEBUG')
        
    def log(self, message, level=None):
        if not level:
            level = '[LVL]'
        if level.upper() in ['DEBUG', 'TEST'] and not self.debug:
            return
        timestamp = datetime.datetime.now()
        output = '%s %s: %s (%s)\n' % (timestamp.isoformat(), level.upper(), message, self.source)
        self.log_file.write(output)
        self.log_file.flush()
        return

if __name__ == '__main__':
    logger = Logger()
    logger.debug = True
    logger.log('--', 'DEBUG')
    logger.log('this is a test log message.', 'DEBUG')
    logger.log('--')


