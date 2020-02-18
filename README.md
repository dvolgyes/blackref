# Blackref: an uncompromising BibTeX formatter

Travis build: [![Build Status](https://travis-ci.org/dvolgyes/blackref.svg?branch=master)](https://travis-ci.org/dvolgyes/blackref)
Coverage: [![Coverage Status](https://img.shields.io/coveralls/github/dvolgyes/blackref/master)](https://img.shields.io/coveralls/github/dvolgyes/blackref/master)

BibTeX files are sometimes hard to read for human beings.
I decided to start two pet project of my own:
 - reflint for checking BibTeX files, fixing fields, but not changing formatting
 - blackref for fixing the BibTeX code style, but not changing any content
   (not counting formatting changes, e.g. ISBN formatting)

Ideally, reflint fixes / warns about missing fields, incorrect values,
and blackref formats everything nicely, but does not do any semantic changes.

Both of them should run both as a command line tool or as a pre-commit hook.
(work in progress)
