collective.base64imagepatch
===========================

The current package: collective.base64imagepatch is an add on for the CMS Plone.
It injects a eventhandlers for Contenttype creation and modification to assure
that no inline base64 encoded image is stored in an RichtTextField.

.. contents:

collective.base64imagepatch Installation
----------------------------------------

Dependencies
------------

There are two soft dependencies on the underlaying Content-Types-Frameworks of
Plone.
* Archetypes
* Dexterity
None of those must be included seperatly in the buildout, as they are already
part of Plone.


Installation via zc.buildout
----------------------------
If you are using zc.buildout to manage your Zope/Plone Instances, you can do
this:

* Add ``collective.base64imagepatch`` to the list of eggs to install, e.g.:

::

    [buildout]
    ...
    eggs =
        ...
        collective.base64imagepatch
        ...

* Re-run buildout, e.g. with:

::

    $ ./bin/buildout


The patch is installed and works directly on next startup.

Note: The patch will not show up in any install listing.

To run patch on existing content call patch_all view on any Plone object for
just this Plone Site Instance or any Zope Root Object for all Plone Sites.
cmf.ManagePortal Permissions required.


Credits
=======

* Contributers:

 * Alexander Loechel

 * Maurits van Rees
