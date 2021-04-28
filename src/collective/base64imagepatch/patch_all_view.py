# -*- coding: utf-8 -*-

from collective.base64imagepatch import logger
from collective.base64imagepatch.patch import patch_object
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView


class PatchAllView(BrowserView):
    """
    Patch Browser View for all portals
    """

    def apply_patch_on_plone_instance(self, portal):
        """
        Apply patch on all content object on package installation
        """

        catalog = getToolByName(portal, "portal_catalog")

        # query catalog for all content objects that
        # provide IContentish interface
        all_brains = catalog(object_provides=IContentish.__identifier__)

        # call patch method for all content objects
        for brain in all_brains:
            info = "Patch Object: %s at path: %s" % (brain.id, brain.getPath())
            self.request.response.write(info + "\n")
            self.request.response.flush()
            logger.debug(info)
            obj = brain.getObject()
            patch_object(obj)

    def patch_instance(self, portal):
        info = "Starting patching Plone Instance: %s at path: %s" % (
            portal.id,
            portal.absolute_url(),
        )
        self.request.response.write(str(info + "\n"))
        self.request.response.flush()
        logger.info(info)

        self.apply_patch_on_plone_instance(portal)

        info = "Finished patching Plone Instance: %s at path: %s\n" % (
            portal.id,
            portal.absolute_url(),
        )
        self.request.response.write(info + "\n")
        self.request.response.flush()
        logger.info(info)

    def search(self, context):
        for item in context.values():
            if item.meta_type == "Plone Site":
                self.patch_instance(item)
            if "Folder" in item.meta_type:
                self.search(item)

    def __call__(self):
        logger.info("Start Patch All")

        context = self.context

        while not context.isTopLevelPrincipiaApplicationObject:
            logger.debug("current Path: " + context.absolute_url())
            if context.meta_type == "Plone Site":
                self.patch_instance(context)
                break
            else:
                context = context.getParentNode()

        self.search(context)
        logger.info("Finished Patch All\n\n")

        return "Finished Patch All"
