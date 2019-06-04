# Blackref: an uncompromising BibTeX formatter

BibTeX files are sometimes hard to read for human beings.
I decided to start two pet project of my own:
 - reflint for checking bibtex files, but not changing formatting
 - blackref for fixing the bibtex code style, but not changing any content
   (not counting formatting changes, e.g. ISBN formatting)

Ideally, reflint fixes / warns about missing fields, incorrect values,
and blackref formats everything nicely, but does not do any semantic changes.
