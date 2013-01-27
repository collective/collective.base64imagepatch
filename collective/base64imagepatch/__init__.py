# -*- extra stuff goes here -*-

from bs4 import BeautifulSoup

from Acquisition import aq_inner

from zope.component import getMultiAdapter
from zope.app.component.hooks import getSite

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
    logger.debug( "patching object " + obj.absolute_url() )   
    
    container = obj.getParentNode()
    if container.isPrincipiaFolderish:
        
        logger.debug( "Object Parent is " + container.absolute_url() )  
        
        for field in obj.schema.fields():
            
            logger.debug( "Object Field is " + field.getType() )  
            if field.getType() == "plone.app.textfield.RichText":
                logger.debug( "object " + obj.title + " is a Dexterity Type" )  
                field_content = field.raw
                if "base64" in field_content:
                    patch(container, obj, field)
            if field.getType() == "Products.Archetypes.Field.TextField":
                logger.debug( "object " + obj.title + " has a field: " + field.getName() + " that is a Archetype TextField that could hold html" )
                field_content = field.getRaw(obj)
                if "base64" in field_content:
                    patch(container, obj, field)
    
    
def patch(container, obj, field):
    """ Original Patch for both """
    counter = 0    
    logger.debug( "patching object: " + obj.absolute_url() +" field: " + field.getName() )
    soup = BeautifulSoup(field.getRaw(obj))
    all_images = soup.find_all('img')
    
    for item in container.keys():
        if item.startswith(obj.id + "." + field.getName() + ".image"):
            counter += 1
    
    for img_tag in all_images:
        if img_tag['src'].startswith('data'):
            image_params = img_tag['src'].split(';')
            mime_type = image_params[0][5:]
            img_data = image_params[1][7:]
            
            img_id = obj.id + "." + field.getName() + ".image" + str(counter)
            
            logger.debug("found img with mime-type: " + mime_type)
                
            #create File in Container with base-name.image# 
            container.invokeFactory("Image", id=img_id, mime_type=mime_type, image=base64.b64decode(img_data))
            new_image = container[img_id]
            
            ## set src attribute to new src-location
            img_tag['src'] = new_image.absolute_url()
            counter += 1
    
    
    if counter > 0:
        field.getMutator(obj)(soup.prettify())
    