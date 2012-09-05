# Introduction

`sqlitemaker` is a tool for converting csv data to sqlite databases. It is 
written in [Python][python] using lots of ugly hacks, with some 
[SQLAlchemy][sqlalchemy] ORM-sauce sprinkled on top. 

This is an old hack I wrote while learning how to write python. I'm sure there 
are a lot of laughable hacks and other ugly corners, but it _does_ work. I still 
use it quite often, and for many more tasks than I originally intended. YMMV.

To see the man-style help documentation, simply run `python sqlitemaker.py -h` 

# Feedback

Drop me a line and let me know if this project is of interest to you, or if you
have any questions: [calebhailey@gmail.com](mailto:calebhailey@gmail.com)

# ToDo

1. Add ability to check for existence of field, add it if it's missing.
2. Parse CSV

[python]: http://www.python.org "Python"
[sqlalchemy]: http://www.sqlalchemy.org/ "SQLAlchemy - The Database Toolkit for Python"


