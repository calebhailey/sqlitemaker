# stlib imports
import argparse
import sys

# local imports
from Common import dotdict, Logger

# naughty global variables
default_prog = 'application'
default_help = '...coming soon...'

class Options():
    """ A wrapper on the stlib argparse module (plus some other extras), to
        make it easy to dynamically add command line options to other scripts.
    """
    def __init__(self, prog=default_prog, add_help=True, log_file=None, debug=False):
        self.logger = Logger(log_file, debug, 'Options.logger')
        self.groups = dotdict({})
        self.options = dotdict({})
        self.parser = argparse.ArgumentParser(prog=prog, add_help=add_help)

    def addGroup(self, name, description=''):
        self.groups[name] = self.parser.add_argument_group(title=name, description=description)
        return self.groups[name]
    
    def editGroup(self, name, property, value):
        self.groups[name].__dict__[property] = value

    def addOption(self, group, name, dest, default=None, help=default_help, choices=False, type=False, required=False, metavar=False, action='store'):
        if not self.groups.has_key(group):
            self.addGroup(group)
        self.options[dest] = self.groups[group].add_argument(name, dest=dest, default=default, help=help)
        if choices: self.editOption(dest, 'choices', choices)
        if type: self.editOption(dest, 'type', type)
        if required: self.editOption(dest, 'required', required)
        if metavar: self.editOption(dest, 'metavar', metavar)
        if action: self.editOption(dest, 'action', action)
        return self.options[dest]

    def editOption(self, name, property, value):
        self.options[name].__dict__[property] = value

    def parseArgs(self, input=None):
        self.arguments = self.parser.parse_args(input)
        return self.arguments

if __name__ == '__main__':
    # run some tests
    option = Options(prog='foo')
    option.logger.debug = True
    option.addGroup('Input Options', 'Input options description...')
    option.addOption('Input Options', '-i --input', 'input', help='input data help...', default=42)
    option.addOption('Output Options', '-o --output', 'output', help='output data help...', default=42)
    option.parseArgs()
    option.logger.log('--', 'DEBUG')
    option.logger.log('arguments: %s' % (option.arguments.__dict__), 'DEBUG')
    option.logger.log('python version: %s' % (sys.version.replace('\n', ' ')), 'DEBUG')
    option.logger.log('--', 'DEBUG')


