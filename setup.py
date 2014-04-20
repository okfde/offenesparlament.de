from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='offenesparlament',
      version=version,
      description="Legislative tracking for the German federal parliaments",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='politics parliament laws tracking flask',
      author='Friedrich Lindenberg',
      author_email='friedrich@pudo.org',
      url='http://okfn.de',
      license='AGPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
