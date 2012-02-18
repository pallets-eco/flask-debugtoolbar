Changes
=======

0.6.2 (2012-02-18)
------------------

Fixes:

- Installation issue on Windows with trailing slashes in MANIFEST.in

- JavaScript error when using conditional comments for ``<html>`` tag
  (like in HTML5 Boilerplate)


0.6.1 (2012-02-15)
------------------

Fixes:

- Memory leak when toolbar was enabled

- UnicodeDecodeError when request data contained binary data (e.g. session values)


Enhancements:

- ``DEBUG_TB_ENABLED`` config setting to explicitly enable or disable the toolbar

- ``DEBUG_TB_HOSTS`` config setting to enable toolbar only for specific remote hosts

- New logo for Flask instead of Django

- Monospaced font on table data

Thanks to kennethreitz and joeshaw for their contributions.


0.6 (2012-01-04)
----------------

Flask 0.8 or higher is required

Enhancements:

- Flask 0.8 compatibility

Thanks to mvantellingen
