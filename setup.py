from setuptools import find_packages
from setuptools import setup


with open("README.rst") as myfile:
    readme = myfile.read()
with open("CHANGES.rst") as myfile:
    changes = myfile.read()

version = "0.13"

setup(
    name="collective.base64imagepatch",
    version=version,
    description="Turn inline images in rich text into actual image objects",
    long_description=readme + "\n" + changes,
    # Get more strings from https://pypi.org/classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords="zope plone base64 image patcher",
    author="Alexander Loechel",
    author_email="Alexander.Loechel@lmu.de",
    url="https://github.com/collective/collective.base64imagepatch",
    license="GPL",
    packages=find_packages("src", exclude=["ez_setup"]),
    package_dir={"": "src"},
    namespace_packages=["collective"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "beautifulsoup4",
    ],
    extras_require={
        "test": [
            "Products.PloneTestCase",
            "plone.app.testing[robot]",
            "plone.app.robotframework",
            "Products.ATContentTypes",
            "Products.contentmigration",
            "plone.app.contenttypes",
        ],
    },
    entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
    setup_requires=["PasteScript"],
    paster_plugins=["ZopeSkel"],
)
