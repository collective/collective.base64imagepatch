# -*- coding: utf-8 -*-

from Acquisition import aq_parent
from bs4 import BeautifulSoup
from collective.base64imagepatch import HAS_ARCHETYPES
from collective.base64imagepatch import HAS_DEXTERITY
from collective.base64imagepatch import logger
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.schema import getFieldsInOrder

import base64
import re


try:
    from zope.component.hooks import getSite
except ImportError:
    from zope.app.component.hooks import getSite


if HAS_ARCHETYPES:
    from Products.Archetypes.interfaces.base import IBaseContent

if HAS_DEXTERITY:
    from plone.dexterity.interfaces import IDexterityContent
    from plone.dexterity.utils import iterSchemata
    from plone.app.textfield.interfaces import IRichText
    from plone.app.textfield.value import RichTextValue


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
                        (obj.title, name),
                    )
                    field_content = field.getRaw(obj)
                    if "base64" in field_content:
                        path = "/".join(obj.getPhysicalPath())
                        logger.debug(
                            "Found inline image in TextField %s of Archetypes object at %s",
                            name,
                            path,
                        )
                        new_content = patch(container, obj, name, field_content)
                        field.getMutator(obj)(new_content)
                        logger.info("Created image for Archetypes object at %s", path)

        elif HAS_DEXTERITY and IDexterityContent.providedBy(obj):
            # Dexterity Object
            for schema in iterSchemata(obj):
                fields = getFieldsInOrder(schema)
                for name, field in fields:
                    if not IRichText.providedBy(field):
                        continue
                    attribute = getattr(obj, name, None)
                    if attribute is None:
                        continue
                    field_content = attribute.raw
                    if "base64" in field_content:
                        path = "/".join(obj.getPhysicalPath())
                        logger.debug(
                            "Found inline image in rich text field %s of Dexterity object at %s",
                            name,
                            path,
                        )
                        new_content = patch(container, obj, name, field_content)
                        setattr(
                            obj,
                            name,
                            RichTextValue(
                                raw=new_content,
                                mimeType=attribute.mimeType,
                                outputMimeType=attribute.outputMimeType,
                                encoding=attribute.encoding,
                            ),
                        )
                        logger.info("Created image for Dexterity object at %s", path)

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
        item.image = NamedBlobImage(
            data=image_data, contentType=mime_type, filename=safe_unicode(id)
        )
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


def patch(container, obj, name, content="", tries=2):
    """
    Original Patch for both:
    * Archetypes
    * Dexterity

    With tries=2: if adding an image to the container fails,
    we do a second try on the parent container.
    """
    if container is not None:
        counter = 0
        logger.debug(
            "Patching Object '%s' on path: %s field: %s content length = %s",
            obj.title,
            obj.absolute_url(),
            name,
            str(len(content)),
        )
        base_html_doc = "<html><head></head><body>%s</body></html>" % content

        soup = BeautifulSoup(base_html_doc, features="lxml")

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
                try:
                    new_image = createImage(
                        container, img_id, mime_type, base64.b64decode(img_data)
                    )
                except ValueError as orig_exc:
                    # Probably: Disallowed subobject type: Image
                    # We can try the parent container, but we should start over completely then.
                    # We try this once.
                    tries -= 1
                    if tries <= 0:
                        logger.info("Adding image failed, no more tries left.")
                        raise
                    # If an image has already been added, this means there is something
                    # wrong only with the current image.
                    if counter:
                        raise
                    orig_path = "/".join(container.getPhysicalPath())
                    logger.debug(
                        "Got ValueError adding Image %s to container at %s. "
                        "Trying in parent of this container.",
                        img_id,
                        orig_path,
                    )
                    try:
                        content = patch(
                            aq_parent(container),
                            obj,
                            name,
                            content=content,
                            tries=tries,
                        )
                        logger.info(
                            "Got ValueError adding Image to container at %s. "
                            "Successfully added in the parent of this container instead.",
                            orig_path,
                        )
                        return content
                    except ValueError:
                        # The second try failed.
                        logger.exception(
                            "Got ValueError adding Image %s to container at %s. "
                            "Trying in parent failed as well.",
                            img_id,
                            orig_path,
                        )
                        # Raise the original exception.
                        raise orig_exc

                # set src attribute to new src-location
                # new_image.relative_url_path() includes Portal-Name
                # id is correct, as it is directly in the same container as
                # the modified object
                img_tag["src"] = new_image.id
                counter += 1
                logger.info(
                    "Created image at %s" % "/".join(new_image.getPhysicalPath())
                )

        if counter > 0:
            content = "".join(str(n) for n in soup("body", limit=1)[0].contents)

        logger.debug("New Content of Object %s:\n%s" % (obj.absolute_url(), content))
    return content
