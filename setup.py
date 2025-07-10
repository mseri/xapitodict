from setuptools import setup

setup(name='xapitodict',
      version='0.5.4',
      packages=['xapitodict', 'xapitodict.cmd'],
      install_requires=["sexpdata", "xmltodict", "setuptools"],
      entry_points={
          'console_scripts': [
              'xapi-to-json = xapitodict.cmd.xapitojson:main'
          ]
      })
