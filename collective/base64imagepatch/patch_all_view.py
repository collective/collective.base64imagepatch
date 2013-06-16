# -*- coding: utf-8 -*-

from collective.base64imagepatch import logger
from collective.base64imagepatch.patch import patch_object  


## Patch Browser View for all portals

    
def setupVarious(context):
    """ 
    Miscellanous steps import handle
    """

    if context.readDataFile('collective.base64imagepatch_various.txt') is None:
        return
    apply_patch_on_install()
    
def apply_patch_on_install():
    """ 
    Apply patch on all content object on package installation 
    """
    
    ## get site_root and portal_catalog
    portal = getSite()
    catalog = getToolByName(portal, 'portal_catalog')

    ## query catalog for all content objects that provide IContentish interface
    all_objects = catalog(object_provides=IContentish.__identifier__)

    ## call patch method for all content objects
    for obj in all_objects:
        patch_object(obj)
 