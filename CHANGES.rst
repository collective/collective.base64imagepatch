Changelog
=========


0.13 (unreleased)
-----------------

- When adding image fails, try the parent container once.  [maurits]

- Fixed patch_all to run patch on objects, not brains.  [maurits]

- BeautifulSoup: always use lxml.  [maurits]

- Fixed for Dexterity on Plone 4.3.  [maurits]


0.12 (2013-11-05)
-----------------

- update patch_all to fix errors on patch_all view where String Formating has failed due to syntax errors

0.11 (2013-07-04)
-----------------

- updated setup.py for Homepage and fixed History
- updated setup.py so that beautifulsoup4 is a dependency that is installed
- remove soft dependency for BeautifulSoup 3 and usage as beautifulsoup4 could
  be used in parallel
- refactor beautifulsoup calls so that it works with all versions of
  beautifulsoup4 (checked with 4.0.1 4.1.0 4.1.3 4.2.0 4.2.1)

0.10 (2013-07-02)
-----------------

- Fixed getSite import and interface for zcml dependency on Plone 4.3


0.9 (2013-06-25)
----------------

- Initial release
