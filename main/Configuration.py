#!/usr/bin/env python
#

""" A wrapper on the python stlib ConfigParser to read and write config settings
    to/from Microsoft Windows-style INI files.

    Links:

    http://docs.python.org/library/configparser.html
    http://en.wikipedia.org/wiki/INI_file

    Example usage:

        from Configuration import Configuration
        config = Configuration(application='.foo', settings='/path/to/application/default/settings.ini')
        config.readSettingsFiles()
        print config.environment   # python dict of environment settings
        print config.default       # python dict of application default settings
        config.writeSettingsFile() # writes settings to users settings file
        
    NOTE: the settings= variable is required even if no default settings file 
    exists, as this variable is used as the file name for reading and/or
    writing the user settings file.

"""

# stlib modules
import ConfigParser
import os
from exceptions import *

# naughty global variables (defaults)
default_application = 'application'
default_settings_file = 'settings.ini'


class Configuration():
    """ A class that can be used to configure the user environment, and
        application settings.  This is mostly just a wrapper on the stlib
        ConfigParser module, plus some other little tidbits I use a lot.

    """
    def __init__(self, application=default_application, settings_file=default_settings_file):
        """ Initialize the configuration instance.
        """
        self.environment = {}
        self.environment['user_home'] = os.path.expanduser('~')
        self.environment['user_desktop'] = os.path.join(self.environment['user_home'], 'Desktop')
        self.environment['application'] = application
        self.environment['default_settings_file'] = settings_file
        self.environment['user_application_dir'] = os.path.join(self.environment['user_home'], self.environment['application'])
        self.environment['user_settings_file'] = os.path.join(self.environment['user_application_dir'], os.path.split( self.environment['default_settings_file'])[1] )
        self.environment['settings_files'] = [self.environment['default_settings_file'], self.environment['user_settings_file']]
        self.default = {}


    def readSettingsFiles(self):
        """ Read settings from the settings file...  Can be run subsequent to
            settings file changes (e.g. if settings file changes after initial
            method execution).
        """
        parser = ConfigParser.RawConfigParser()
        parser.read(self.environment['settings_files']) # read whatever settings files we know about (default and/or user settings)
        for section in parser.sections():
            self.default[section] = {}
            for setting, value in parser.items(section):
                self.default[section][setting] = value
        return self.default


    def writeSettingsFile(self, file=None):
        """ Write the settings file.
        """
        if file == None:
            file = self.environment['user_settings_file']
        if not os.path.exists(self.environment['user_application_dir']):
            try:
                os.makedirs(self.environment['user_application_dir'])
            except:
                raise NotImplementedError
        config = ConfigParser.RawConfigParser()
        for section in self.default:
            config.add_section(section)
            for setting in self.default[section]:
                value = self.default[section][setting]
                config.set(section, setting, value)
        settings_file = open(file, 'w')
        config.write(settings_file)
        settings_file.flush()
        settings_file.close()
        return file, self.default


if __name__ == '__main__':
    settings = Configuration(application='test')
    settings.readSettingsFiles()
    print settings.environment
    print settings.default

