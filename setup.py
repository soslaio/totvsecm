# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='totvsecm',
      version='1.0',
      description='API para webservices do TOTVS ECM.',
      url='http://github.com/soslaio/totvsecm',
      author='soslaio',
      author_email='contato@soslaio.com',
      license='MIT',
      packages=['zeep'],
      install_requires=[
          'zeep',
      ],
      zip_safe=False)
