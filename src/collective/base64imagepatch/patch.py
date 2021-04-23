# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from collective.base64imagepatch import HAS_ARCHETYPES
from collective.base64imagepatch import HAS_DEXTERITY
from collective.base64imagepatch import logger
from Products.CMFCore.utils import getToolByName

import base64
import re
import zope.interface
import zope.schema


try:
    from zope.component.hooks import getSite
except ImportError:
    from zope.app.component.hooks import getSite


if HAS_ARCHETYPES:
    from Products.Archetypes.interfaces.base import IBaseContent

if HAS_DEXTERITY:
    from plone.dexterity.interfaces import IDexterityContent


def patch_object(obj):

    logger.debug('Patching Object "%s" on path: %s', (obj.title, obj.absolute_url()))

    container = obj.getParentNode()

    if container and container.isPrincipiaFolderish:
        logger.debug("Object Type is %s", obj.portal_type)
        logger.debug("Object Parent is %s", container.absolute_url())

        if HAS_ARCHETYPES and IBaseContent.providedBy(obj):
            # Archetype Object
            for field in obj.schema.fields():
                if field.getType() == "Products.Archetypes.Field.TextField":
                    name = field.getName()
                    logger.debug(
                        'Object "%s" is a Archetypes Type that has a field: "%s" that is a Archetype TextField that could hold HTML',
                        (obj.title, field.getName()),
                    )
                    field_content = field.getRaw(obj)
                    if "base64" in field_content:
                        new_content = patch(container, obj, name, field_content)
                        field.getMutator(obj)(new_content)

        elif HAS_DEXTERITY and IDexterityContent.providedBy(obj):
            # Dexterity Object
            pt = obj.getTypeInfo()
            schema = pt.lookupSchema()
            for name in zope.schema.getFields(schema).keys():
                logger.debug("Object Field Name is %s", name)
                logger.debug(
                    "Object Field Type is %s", str(type(getattr(obj, name)).__name__)
                )

                if type(getattr(obj, name)).__name__ == "RichTextValue":
                    logger.debug("object %s is a Dexterity Type", obj.title)
                    field_content = getattr(obj, name).raw
                    if "base64" in field_content:
                        new_content = patch(container, obj, name, field_content)

                        getattr(obj, name).__init__(raw=new_content)
        else:
            logger.debug("Unknown Content-Type-Framework for %s", obj.absolute_url())


def createImage(container, id, mime_type=None, image_data=None):
    # Base assumption: An Image Type is avaliable
    portal = getSite()
    portal_types = getToolByName(portal, "portal_types")

    if portal_types.Image.meta_type == "Dexterity FTI":
        # assumption: plone.app.contenttypes Image
        logger.debug("Images are 'Dexterity FTI' Types")
        # from plone.dexterity.utils import createContentInContainer
        from plone.namedfile.file import NamedBlobImage

        # item = createContentInContainer(
        #    container,
        #    "Image",
        #    title=id,
        #    id=id,
        #    image=image_data
        #    )
        # return item

        container.invokeFactory("Image", title=id, id=id)
        item = container[id]

        # pt = item.getTypeInfo()
        # schema = pt.lookupSchema()

        # assumes, that the Image Type has a field image
        # that is a NamedBlobImage
        item.image = NamedBlobImage(data=image_data, contentType=mime_type, filename=id)

        return item

    elif (
        portal_types.Image.Metatype() == "ATBlob"
        or portal_types.Image.Metatype() == "ATImage"
    ):

        logger.debug('Images are "Archetypes" Types')
        container.invokeFactory(
            "Image", id=id, title=id, mime_type=mime_type, image=image_data
        )
        return container[id]

    else:
        logger.warn("Unknown Factory or Invocation for Image")
        logger.warn("Image has Meta-Type: %s", portal_types.Image.meta_type)
    return None


def patch(container, obj, name, content=""):
    """
    Original Patch for both:
    * Archetypes
    * Dexterity
    """
    if container is not None:
        counter = 0
        logger.debug(
            'Patching Object "%s" on path: %s field: %s content length = %s',
            (obj.title, obj.absolute_url(), name, str(len(content))),
        )
        base_html_doc = "<html><head></head><body>%s</body></html>" % content

        soup = BeautifulSoup(base_html_doc)

        all_images = soup(src=re.compile("(data:).*(;base64,).*"))
        suffix_list = []
        suffix = obj.id + "." + name + ".image"
        for item in container.keys():

            if item.startswith(suffix):
                suffix_list.append(int(item[len(suffix) :]))
                counter += 1
        suffix_list.sort()
        counter = max(suffix_list) + 1 if len(suffix_list) > 0 else 0

        for img_tag in all_images:
            if (
                hasattr(img_tag, "src")
                and img_tag["src"].startswith("data")
                and "base64" in img_tag["src"]
            ):

                image_params = img_tag["src"].split(";")
                mime_type = image_params[0][len("data:") :]
                if mime_type == "":
                    mime_type = None
                else:
                    logger.debug(
                        "Found image <img > with mime-type: %s", str(mime_type)
                    )
                img_data = image_params[1][len("base64,") :]
                img_id = suffix + str(counter)

                # create File in Container with base-name.image#
                # container.invokeFactory(
                #    "Image",
                #    id=img_id,
                #    mime_type=mime_type,
                #    image=base64.b64decode(img_data))
                new_image = createImage(
                    container, img_id, mime_type, base64.b64decode(img_data)
                )

                # set src attribute to new src-location
                # new_image.relative_url_path() includes Portal-Name
                # id is correct, as it is directly in the same container as
                # the modified object
                img_tag["src"] = new_image.id
                counter += 1

        if counter > 0:
            content = "".join(str(n) for n in soup("body", limit=1)[0].contents)

        logger.debug("New Content of Object %s:\n%s" % (obj.absolute_url(), content))
    return content
