# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

import logging
import base64
import pkg_resources
import zope.interface
import zope.schema

try: 
    from zope.component.hooks import getSite
except:
    from zope.app.component.hooks import getSite

#try:
#    from bs4 import BeautifulSoup
#except: 
#    from BeautifulSoup import BeautifulSoup

try:
    pkg_resources.get_distribution('beautifulsoup4')
except pkg_resources.DistributionNotFound:
    pass
else:
    from bs4 import BeautifulSoup

try:
    pkg_resources.get_distribution('BeautifulSoup')
except pkg_resources.DistributionNotFound:
    pass
else:
    from BeautifulSoup import BeautifulSoup

try:
    pkg_resources.get_distribution('Products.Archetypes')
except pkg_resources.DistributionNotFound:
    HAS_ARCHETYPES = False
else:
    HAS_ARCHETYPES = True
    from Products.Archetypes.interfaces.base import IBaseContent

try:
    pkg_resources.get_distribution('plone.dexterity')
except pkg_resources.DistributionNotFound:
    HAS_DEXTERITY = False
else:
    HAS_DEXTERITY = True
    from plone.dexterity.interfaces import IDexterityContent

logger = logging.getLogger('patch_base64images')

def initialize(context):
    """
    Initializer called when used as a Zope 2 product.
    """
    
def setuphandler():
    """

    """
    
   
def patch_base64_images_on_create(context, event):
    """ 
    Patch created content if it contains an inline images coded as base64 
    """
    patch_object(context)

    
def patch_base64_images_on_modifiy(context, event):
    """ 
    Patch created content if it contains an inline images coded as base64 
    """
    patch_object(context)

    
def apply_patch_on_install():
    """ 
    Apply patch on all content object on package installation 
    """
    
    #get site_root
    portal = getSite()
    catalog = getToolByName(portal, 'portal_catalog')

    all_objects = catalog(object_provides=IContentish.__identifier__)

    for obj in all_objects:
        patch_object(obj)
        
def patch_object(obj):
    
    logger.info( 
        "Patching Object \"" + 
        obj.title + 
        "\" on path: " + 
        obj.absolute_url() 
        )   
    
    container = obj.getParentNode()
    
    if container and container.isPrincipiaFolderish:
        logger.info( "Object Type is " + obj.portal_type)
        logger.info( "Object Parent is " + container.absolute_url() ) 
        
        if HAS_ARCHETYPES and IBaseContent.providedBy(obj):
            # Archetype Object
            for field in obj.schema.fields():
                if field.getType() == "Products.Archetypes.Field.TextField":
                    name = field.getName()
                    logger.info( 
                        "Object \""+obj.title+"\" is a Archetypes Type"+
                        " that has a field: \"" + field.getName() + 
                        "\" that is a Archetype TextField that could hold HTML" 
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
                logger.info( "Object Field Name is " + name )
                logger.info( "Object Field Type is " + 
                    str( type( getattr(obj, name) ).__name__ ) ) 
                
                if type(getattr(obj, name)).__name__ == "RichTextValue":
                    logger.info( "object "+obj.title+" is a Dexterity Type" )  
                    field_content = getattr(obj, name).raw
                    if "base64" in field_content:
                        new_content = patch(container, obj, name, field_content)
                        
                        getattr(obj, name).__init__(raw=new_content)
        else:
            logger.info( "Unknown Content-Type-Framework for " + 
                obj.absolute_url() 
                )

def createImage(container, id, mime_type=None, image_data=None):
    # Base assumtion: An Image Type is avaliable
    portal = getSite()
    portal_types = getToolByName(portal, "portal_types")
    if portal_types.Image.meta_type == "Dexterity FTI":
        # assumtion: plone.app.contenttypes Image 
        logger.info("Images are \"Dexterity FIT\" Types")
        #from plone.dexterity.utils import createContentInContainer
        from plone.namedfile.file import NamedBlobImage 
        #item = createContentInContainer(
        #    container, 
        #    "Image", 
        #    title=id, 
        #    id=id, 
        #    image=image_data
        #    )
        #return item

        container.invokeFactory(
                "Image",
                title=id, 
                id=id)
        item = container[id]

        #pt = item.getTypeInfo()
        #schema = pt.lookupSchema()

        # assumes, that the Image Type has a field image 
        # that is a NamedBlobImage
        item.image = NamedBlobImage(
            data=image_data,
            contentType=mime_type,
            filename=id
        ) 

        return item

    elif portal_types.Image.meta_type == "ATBlob" or 
        portal_types.Image.meta_type == "ATImage":

        logger.info("Images are \"Archetypes\" Types")
        container.invokeFactory(
                "Image", 
                id=id, 
                title=id,
                mime_type=mime_type, 
                image=base64.b64decode(img_data))
        return container[id]

    else:
        logger.warn("Unknown Factory or Invocation for Image")
        logger.warn("Image has Meta-Type: " + portal_types.Image.meta_type)
    return None
    
def patch(container, obj, name, content):    
    """ Original Patch for both """
    counter = 0    
    logger.info( "Patching Object \"" + obj.title + 
        "\" on path: " + obj.absolute_url() + " field: " + name )
    soup = BeautifulSoup(content)
    all_images = soup.find_all('img')
    suffix_list = []
    suffix = obj.id + "." + name + ".image"
    for item in container.keys():
        
        if item.startswith(suffix):
            suffix_list.append(int(item[len(suffix):]))
            counter += 1
    suffix_list.sort()
    counter = max(suffix_list) + 1 if len(suffix_list) > 0 else 0

    for img_tag in all_images:
        if img_tag['src'].startswith('data'):
            image_params = img_tag['src'].split(';')
            mime_type = image_params[0][len("data:"):]
            img_data = image_params[1][len("base64,"):]
            img_id = suffix + str(counter)
            
            logger.info("Found image <img > with mime-type: " + mime_type)
                
            # create File in Container with base-name.image# 
            #container.invokeFactory(
            #    "Image", 
            #    id=img_id, 
            #    mime_type=mime_type, 
            #    image=base64.b64decode(img_data))
            new_image = createImage(
                container, 
                img_id, 
                mime_type, 
                base64.b64decode(img_data))

            ## set src attribute to new src-location
            ## new_image.relative_url_path() includes Portal-Name
            ## id is correct, as it is directly in the same container as 
            ## the modified object
            img_tag['src'] = new_image.id 
            counter += 1
    
    if counter > 0:
        content = soup.find("body").contents[0].prettify()
        
    logger.info("New Content of Object "+obj.absolute_url()+":\n" + content)
    return content
    