# -*- coding: utf-8 -*-

from collective.base64imagepatch import logger
from collective.base64imagepatch.patch import patch_object  
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

## Patch Browser View for all portals
    
class PatchAllView(BrowserView):


    def apply_patch_on_plone_instance(self,portal):
        """ 
        Apply patch on all content object on package installation 
        """
        
        ## get site_root and portal_catalog
        logger.info("Patch Plone Site: " + portal.id + 
                    " at path: " + portal.absolute_url())  

        catalog = getToolByName(portal, 'portal_catalog')

        ## query catalog for all content objects that provide IContentish interface
        all_objects = catalog(object_provides=IContentish.__identifier__)

        ## call patch method for all content objects
        for obj in all_objects:
            patch_object(obj)

    def search(self,context):
        for item in context.values():
            if item.meta_type == "Plone Site":
                self.apply_patch_on_plone_instance(item)
                print "\nPlone Instance: " + item.id + " at path: " \
                    + item.absolute_url() + " patched"
            if "Folder" in item.meta_type:
                self.search(item)

    def __call__(self):
        logger.info("Patch All")

        context = self.context

        print "Start Patch All Script"
        while not context.isTopLevelPrincipiaApplicationObject:
            logger.info("current Path: " + context.absolute_url())
            if context.meta_type == "Plone Site":
                self.apply_patch_on_plone_instance(context)
                print "\nPlone Instance: " + context.id + " at path: " \
                    + context.absolute_url() + " patched"
                break
            else:
                context = context.getParentNode()

        self.search(context)

        print "\n\nPatch All finished"
        return printed



     