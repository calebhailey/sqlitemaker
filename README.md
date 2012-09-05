# Introduction
**SqliteMaker** is a tool for converting csv data to sqlite databases. It is 
written in [Python][python] using ugly hacks with some [SQLAlchemy][sqlalchemy] 
ORM-sauce sprinkled on top. 

This is an old tool I wrote while learning how to write python (perhaps my first
complete python project). I've recently tried my hand at a rewrite so that the 
code is a little less embarassing, but I'm sure there are still some laughable 
hacks and other ugly corners... having said that - it _does_ work. I still use 
this quite often in my daily analytical work, and for many more tasks than I 
originally intended. YMMV.

To see the man-style help documentation, simply run: 
```
$ python sqlitemaker.py -h
```

# Purpose / Use Cases

I don't know about you, but I despise spreadsheets. It's not just Microsoft 
Excel - it's most any spreadsheet application. Don't get me wrong - they're 
incredibly useful in certain use cases, like creating a document containing 
some simple tabular data, or for slapping together a adhoc calculator of sorts 
for solving some complex math problem... but for data mining? No thanks. Even 
if you only have rudimentary SQL query skills, a database is a _much_ more 
useful venue for analyzing tabular data. Thus the primary use case for this 
tool. 

All too often I found myself needing to take some data in a spreadsheet, or 
other tabular data, and generate some report from it. No amount of spreadsheet 
productivity application wizardry in the world is as handy as what can be 
accomplished with some simple `SELECT` statements in a SQL query. 

## Examples

The most common thing I do with **SqliteMaker** is take an Excel spreadsheet, 
export it as a csv, and convert it to a [SQLite][sqlite] database. From there 
I'll usually open the database using a tool like [Sqliteman][sqliteman] 
(recommended) or [SQLite Database Browser][sqlitebrowser], and use the built-in 
query editors to query for whatever information I'm after. Both tools let you 
export query results as a csv file, so you can get your modified / analyzed 
results back into the original format you started with.

To try this for yourself, copy a csv file into the directory where you have 
downloaded **SqliteMaker** and run: 

```
$ python sqlitemaker.py -i sample.csv
```

# Feedback

Mention me on Twitter at [@calebhailey][calebhailey] or 
[@SQLiteMaker][sqlitemaker], or drop me a line and let me know if this project 
is of interest to you, or if you have any questions: 
[calebhailey@gmail.com](mailto:calebhailey@gmail.com)


[python]: http://www.python.org "Python Home Page"
[sqlalchemy]: http://www.sqlalchemy.org/ "SQLAlchemy - The Database Toolkit for Python"
[sqlite]: http://www.sqlite.org "SQLite Home Page"
[sqliteman]: http://sqliteman.com/ "SQLiteman - SQLite Databases Made Easy"
[sqlitebrowser]: http://sqlitebrowser.sourceforge.net/ "SQLite Database Browser"
[calebhailey]: http://www.twitter.com/calebhailey "Follow me on Twitter"
[sqlitemaker]: http://www.twitter.com/sqlitemaker "Follow my project on Twitter"


