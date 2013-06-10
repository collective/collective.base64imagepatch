collective.base64imagepatch
===========================

The current package: collective.base64imagepatch is an add on for the CMS Plone. 
It injects a eventhandler for Contenttype creation and modification to assure 
that no inline base64 encoded image is stored in an RichtTextField.

.. contents:

collective.base64imagepatch Installation
----------------------------------------

Dependencies
------------

There is a hard dependency for one of these BeautifulSoup packages:
* beautifulsoup4 (new version)
* BeautifulSoup (old depricated version, but usable if already installed or beautifulsoup4 would cause any version conflicts)
One of those both packages have to be installed. As zc.buildout did not allow optional requires statements you have to include it into your dependency-list

There are two soft dependencies on the underlaying Content-Types-Frameworks of Plone. 
* Archetypes
* Dexterity
None of those must be included seperatly in the buildout, as they are already part of Plone.


Installation via zv.buildout
----------------------------
If you are using zc.buildout to manage your Zope/Plone Instances, you can do this:

* Add ``collective.base64imagepatch`` to the list of eggs to install, e.g.:

    [buildout]
    ...
    eggs =
        ...
        collective.base64imagepatch
        beautifulsoup4 or BeautifulSoup
      
* Re-run buildout, e.g. with:

    $ ./bin/buildout


.. include: ./docs/HISTORY.txt

Credits
=======

* Contributers:
** Alexander Loechel