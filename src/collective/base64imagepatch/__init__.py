# -*- coding: utf-8 -*-

import logging
import pkg_resources


try:
    pkg_resources.get_distribution("Products.Archetypes")
except pkg_resources.DistributionNotFound:
    HAS_ARCHETYPES = False
else:
    HAS_ARCHETYPES = True

try:
    pkg_resources.get_distribution("plone.dexterity")
except pkg_resources.DistributionNotFound:
    HAS_DEXTERITY = False
else:
    HAS_DEXTERITY = True

logger = logging.getLogger("patch_base64images")


def initialize(context):
    """
    Initializer called when used as a Zope 2 product.
    """
    pass
