# -*- coding: utf-8 -*-

from collective.base64imagepatch import logger
from collective.base64imagepatch.patch import patch_object  
   
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
