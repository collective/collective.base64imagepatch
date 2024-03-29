from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

# from zope.testing import doctestunit
# from zope.component import testing
from Testing import ZopeTestCase as ztc

import collective.base64imagepatch
import unittest


ptc.setupPloneSite()


class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            pass
            """
            fiveconfigure.debug_mode = True
            ztc.installPackage(collective.base64imagepatch)
            fiveconfigure.debug_mode = False
            """

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite(
        [
            # Unit tests
            # doctestunit.DocFileSuite(
            #    'README.txt', package='collective.base64imagepatch',
            #    setUp=testing.setUp, tearDown=testing.tearDown),
            # doctestunit.DocTestSuite(
            #    module='collective.base64imagepatch.mymodule',
            #    setUp=testing.setUp, tearDown=testing.tearDown),
            # Integration tests that use PloneTestCase
            # ztc.ZopeDocFileSuite(
            #    'README.txt', package='collective.base64imagepatch',
            #    test_class=TestCase),
            # ztc.FunctionalDocFileSuite(
            #    'browser.txt', package='collective.base64imagepatch',
            #    test_class=TestCase),
        ]
    )


if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
