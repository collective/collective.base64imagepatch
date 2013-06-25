# -*- coding: utf-8 -*-

## external imports
from Acquisition import aq_inner
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

import base64
import pkg_resources
import zope.interface
import zope.schema


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

## inner imports
from collective.base64imagepatch import logger
from collective.base64imagepatch import HAS_ARCHETYPES
from collective.base64imagepatch import HAS_DEXTERITY

if HAS_ARCHETYPES:
    from Products.Archetypes.interfaces.base import IBaseContent

if HAS_DEXTERITY:
    from plone.dexterity.interfaces import IDexterityContent
       
def patch_object(obj):

    #import ipdb; ipdb.set_trace();
    
    logger.debug( 
        "Patching Object \"" + 
        obj.title + 
        "\" on path: " + 
        obj.absolute_url() 
        )   
    
    container = obj.getParentNode()
    
    if container and container.isPrincipiaFolderish:
        logger.debug( "Object Type is " + obj.portal_type)
        logger.debug( "Object Parent is " + container.absolute_url() ) 
        
        if HAS_ARCHETYPES and IBaseContent.providedBy(obj):
            # Archetype Object
            for field in obj.schema.fields():
                if field.getType() == "Products.Archetypes.Field.TextField":
                    name = field.getName()
                    logger.debug( 
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
                logger.debug( "Object Field Name is " + name )
                logger.debug( "Object Field Type is " + 
                    str( type( getattr(obj, name) ).__name__ ) ) 
                
                if type(getattr(obj, name)).__name__ == "RichTextValue":
                    logger.debug( "object "+obj.title+" is a Dexterity Type" )  
                    field_content = getattr(obj, name).raw
                    if "base64" in field_content:
                        new_content = patch(container, obj, name, field_content)
                        
                        getattr(obj, name).__init__(raw=new_content)
        else:
            logger.debug( "Unknown Content-Type-Framework for " + 
                obj.absolute_url() 
                )



def createImage(container, id, mime_type=None, image_data=None):
    # Base assumtion: An Image Type is avaliable
    portal = getSite()
    portal_types = getToolByName(portal, "portal_types")
    #import ipdb; ipdb.set_trace()
    if portal_types.Image.meta_type == "Dexterity FTI":
        # assumtion: plone.app.contenttypes Image 
        logger.debug("Images are \"Dexterity FIT\" Types")
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

    elif portal_types.Image.Metatype() == "ATBlob" or \
        portal_types.Image.Metatype() == "ATImage":

        logger.debug("Images are \"Archetypes\" Types")
        container.invokeFactory(
                "Image", 
                id=id, 
                title=id,
                mime_type=mime_type, 
                image=image_data
            )
        return container[id]

    else:
        logger.warn("Unknown Factory or Invocation for Image")
        logger.warn("Image has Meta-Type: " + portal_types.Image.meta_type)
    return None
    
def patch(container, obj, name, content):    
    """ 
    Original Patch for both:
    * Archetypes 
    * Dexterity
    """
    counter = 0    
    logger.debug( "Patching Object \"" + obj.title + 
        "\" \non path: " + obj.absolute_url() + "\nfield: " + name + 
        "\ncontent length = " + str(len(content)) )
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
        if img_tag.has_key('src') and img_tag['src'].startswith('data'):
            image_params = img_tag['src'].split(';')
            mime_type = image_params[0][len("data:"):]
            if mime_type == "":
                mime_type = None
            else:
                logger.debug("Found image <img > with mime-type: " + str(mime_type))                
            img_data = image_params[1][len("base64,"):]
            img_id = suffix + str(counter)
               
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
        content = "".join(str(n) for n in soup.find('body').contents)

        
    logger.info("New Content of Object "+obj.absolute_url()+":\n" + content)
    return content
    