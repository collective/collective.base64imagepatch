# -*- extra stuff goes here -*-


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    
    
    
    
def patch_base64_images_on_create(event):
    """ Patch created content if it contains an inline images coded as base64 """
    

    
def patch_base64_images_on_modifiy(event):
    """ Patch created content if it contains an inline images coded as base64 """

    
def apply_patch_on_install():
    """ Apply patch on all content object on package installation """
    
    #get site_root
    
    for obj in all_objects:
        
        
def patch_object(obj):
    container = obj.parent()
    
    for field in obj.schema.fields():
        if field is RichtTextField:
            field_content = field.value()
            if field_content.contains("base64"):
                
    
    
def patch(container):
    """ Original Patch for both """
    
    
    
    #create File in Container with base-name.image# 