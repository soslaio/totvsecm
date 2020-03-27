
from setuptools import setup

setup(name='totvsecm',
      version='1.1.0',
      description='API para webservices do TOTVS ECM.',
      url='http://github.com/soslaio/totvsecm',
      author='soslaio',
      author_email='rogeriorp@gmail.com',
      license='MIT',
      packages=['totvsecm'],
      install_requires=[
          'zeep',
      ],
      zip_safe=False)
