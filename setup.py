#!/usr/bin/env python

from distutils.core import setup

setup(
      name='SQLiteMaker',
      author='calebhailey',
      url='https://github.com/calebhailey/sqlitemaker',
      packages=['main'],
      py_modules=['sqlitemaker'],
      data_files=[('', ['settings.json',]),],
      requires=['SQLAlchemy'],
      )
