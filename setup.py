
from setuptools import setup

with open('README.md') as fh:
    long_description = re.sub(
        '^.. start-no-pypi.*^.. end-no-pypi', '', fh.read(), flags=re.M | re.S)

setup(name='totvsecm',
      version='1.5.0',
      description='API para webservices do TOTVS ECM.',
      long_description=long_description,
      url='http://github.com/soslaio/totvsecm',
      author='soslaio',
      author_email='rogeriorp@gmail.com',
      license='MIT',
      classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.7',
            'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      packages=['totvsecm'],
      install_requires=[
          'zeep',
      ],
      zip_safe=False)
