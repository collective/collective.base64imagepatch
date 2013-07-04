from setuptools import setup, find_packages
import os

version = '0.12dev'

setup(name='collective.base64imagepatch',
      version=version,
      description="",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='zope plone base64 image patcher',
      author='Alexander Loechel',
      author_email='Alexander.Loechel@lmu.de',
      url='https://github.com/collective/collective.base64imagepatch',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          #'BeautifulSoup', # old version
          #'beautifulsoup4', # new version
          'beautifulsoup4',
      ],
      extras_require={
          'test': [
              'plone.app.testing[robot]',
              'plone.app.robotframework',
              'Products.ATContentTypes',
              'Products.contentmigration',
              'plone.app.contenttypes',
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
