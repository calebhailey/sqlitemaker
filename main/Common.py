# stlib imports
import codecs
import datetime
import json
import sys

# naughty globals
encoding = 'utf-8-sig'

class dotdict(dict):
    def __getattr__(self, attr):
        return self.get(attr, None)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

class Settings(object):
    def __init__(self, settings_file, section=None):
        self.source = settings_file
        self.file = codecs.open(self.source, 'rb', encoding)
        self.settings = dotdict(self.read(section))
        self.file.close()

    def read(self, section):
        self.file = codecs.open(self.file.name, self.file.mode, self.file.encoding)
        self.settings = json.loads(self.file.read())
        self.file.close()
        if section:
            return self.settings[section]
        else:
            return self.settings

class Logger(object):
    def __init__(self, logfile=None, debug=False):
        if logfile:
            self.logfile = logfile
        else:
            self.logfile = sys.stdout
        self.debug = debug
        
    def log(self, message, level=None):
        if not level:
            level = '[LVL]'
        if level.upper() in ['DEBUG', 'TEST'] and not self.debug:
            return
        timestamp = datetime.datetime.now()
        output = '%s %s: %s\n' % (timestamp.isoformat(), level.upper(), message)
        self.logfile.write(output)
        return

if __name__ == '__main__':
    logger = Logger()
    logger.debug = True
    logger.log('--', 'DEBUG')
    logger.log('this is a test log message.', 'DEBUG')
    logger.log('--')


