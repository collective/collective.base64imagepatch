# -*- extra stuff goes here -*-

from bs4 import BeautifulSoup

from Acquisition import aq_inner

from zope.component import getMultiAdapter
try: 
    from zope.component.hooks import getSite
except:
    from zope.app.component.hooks import getSite

import zope.schema
import zope.interface

try: 
    from Products.Archetypes.interfaces.base import IBaseContent
except: 
    pass

try:
    from plone.dexterity.interfaces import IDexterityContent
except:
    pass
    
import logging
import base64


logger = logging.getLogger('patch_base64images')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    
    
    
'''    
def patch_base64_images_on_create(context, event):
    """ Patch created content if it contains an inline images coded as base64 """
    patch_object(context)
'''
    
def patch_base64_images_on_modifiy(context, event):
    """ Patch created content if it contains an inline images coded as base64 """
    patch_object(context)

    
def apply_patch_on_install():
    """ Apply patch on all content object on package installation """
    
    #get site_root
    portal = getSite()
    



    for obj in all_objects:
        patch_object(obj)
        
        
def patch_object(obj):
    
    logger.info( "patching object " + obj.absolute_url() )   
    
    container = obj.getParentNode()
    
    if container and container.isPrincipiaFolderish:
        logger.info( "Object Type is " + obj.portal_type)
        logger.info( "Object Parent is " + container.absolute_url() ) 
        
        if IBaseContent.providedBy(obj):
            # Archetype Object
            for field in obj.schema.fields():
                if field.getType() == "Products.Archetypes.Field.TextField":
                    name = field.getName()
                    logger.info( "object " + obj.title + " has a field: " + field.getName() + " that is a Archetype TextField that could hold html" )
                    field_content = field.getRaw(obj)
                    if "base64" in field_content:
                        new_content = patch(container, obj, name, field_content)
                        field.getMutator(obj)(new_content)

        elif IDexterityContent.providedBy(obj):
            # Dexterity Object
            pt = obj.getTypeInfo()
            schema = pt.lookupSchema()
            for name in zope.schema.getFields(schema).keys():
                logger.info( "Object Field Name is " + name )
                logger.info( "Object Field Type is " + str( type( getattr(obj, name) ).__name__ ) ) 
                
                if type(getattr(obj, name)).__name__ == "RichTextValue":
                    logger.info( "object " + obj.title + " is a Dexterity Type" )  
                    field_content = getattr(obj, name).raw
                    if "base64" in field_content:
                        new_content = patch(container, obj, name, field_content)
                        logger.info("New Content : " + new_content)
                        import ipdb; ipdb.set_trace()
                        #setattr(getattr(obj, name).__init__(raw = new_content)
        else:
            logger.info( "Unknown Content-Type-Framework for " + obj.absolute_url() )
    
def patch(container, obj, name, content):    
    """ Original Patch for both """
    counter = 0    
    logger.info( "patching object: " + obj.absolute_url() + " field: " + name )
    soup = BeautifulSoup(content)
    all_images = soup.find_all('img')
    
    for item in container.keys():
        if item.startswith(obj.id + "." + name + ".image"):
            counter += 1
    
    for img_tag in all_images:
        if img_tag['src'].startswith('data'):
            image_params = img_tag['src'].split(';')
            mime_type = image_params[0][5:]
            img_data = image_params[1][7:]
            
            img_id = obj.id + "." + name + ".image" + str(counter)
            
            logger.info("found img with mime-type: " + mime_type)
                
            #import ipdb; ipdb.set_trace()
            # create File in Container with base-name.image# 
            container.invokeFactory("Image", id=img_id, mime_type=mime_type, image=base64.b64decode(img_data))
            new_image = container[img_id]
            
            ## set src attribute to new src-location
            img_tag['src'] = new_image.absolute_url_path()
            counter += 1
    
    if counter > 0:
        content = soup.find("body").contents[0].prettify()
        
    logger.info("New Content : " + content)
    return content
    