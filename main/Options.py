#!/usr/bin/env python2.7
#

""" A wrapper on the python 2.7+ stlib argparse to dynamically create command
    line options and manage the parsing of said options.

    Example usage:

    from Options import Options
    options = Options(prog='HelloWorld')
    options.addGroup('Input', 'This is the description text for the Input options section')
    options.addOption('Input', '-f --foo', 'foo', help='do something with FOO', default='foobar')

    NOTES: if an option is added to a non-existent group, the group will be
    automatically created (without a description).

"""

# not sure if this is how to do a version check, but it works... :sigh:
from exceptions import *
import argparse
import sys

# naughty global variables
default_prog = 'application'
default_help = '...coming soon...'

# do stuff
class Options():
    """ A wrapper on the stlib argparse module (plus some other extras), to
        make it easy to dynamically add command line options to other scripts.
    """
    def __init__(self, prog=default_prog, add_help=True):
        """ Setup our instance...
        """
        self.groups = {}
        self.options = {}
        self.parser = argparse.ArgumentParser(prog=prog, add_help=add_help)


    def addGroup(self, name, description=''):
        """ Add an option group, and associated documentation.
        """
        self.groups[name] = self.parser.add_argument_group(title=name, description=description)
        return self.groups[name]

    
    def editGroup(self, name, property, value):
        """ Edit a property of an existing group...
        """
        self.groups[name].__dict__[property] = value


    def addOption(self, group, name, dest, default=None, help=default_help, choices=False, type=False, required=False, metavar=False, action='store'):
        """ Add an option to a group, with custom settings.
        """
        if not self.groups.has_key(group):
            # oops, this group doesn't exist... why don't we go ahead and create it & try again...
            self.addGroup(group)
        self.options[dest] = self.groups[group].add_argument(name, dest=dest, default=default, help=help)
        if choices: self.editOption(dest, 'choices', choices)
        if type: self.editOption(dest, 'type', type)
        if required: self.editOption(dest, 'required', required)
        if metavar: self.editOption(dest, 'metavar', metavar)
        if action: self.editOption(dest, 'action', action)
        return self.options[dest]


    def editOption(self, name, property, value):
        """ Edit a property of an existing option...
        """
        self.options[name].__dict__[property] = value


    def parseArgs(self, input=None):
        """ Parse the options...
        """
        return self.parser.parse_args(input)


if __name__ == '__main__':
    options = Options(prog='foo')
    # options.addGroup('Input', 'Input options description...')
    options.addOption('Input Options', '-i --input', 'input', help='input data help...', default=42)
    options.addOption('Output Options', '-o --output', 'output', help='output data help...', default=42)
    arguments = options.parseArgs()

    print 'arguments:', arguments.__dict__
    print '\npython version', sys.version
