from setuptools import setup, find_packages

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='vr900-connector',
      version='0.1.0rc0',
      description='Connector to handle vaillant vr900/vr920 data',
      long_description_content_type='text/markdown',
      long_description=long_description,
      url='https://github.com/thomasgermain/vr900-connector.git',
      author='Thomas Germain',
      author_email='thomas.germain@live.be',
      license='MIT',
      packages=find_packages(exclude=('tests', 'tests/*', '/tests', '/tests/*')),
      zip_safe=False,
      setup_requires=["pytest-runner"],
      install_requires=[
          "requests>=2.20.0,<3.0.0",
          "jsonpickle>=1.0,<2.0"
      ],
      entry_points={
          'console_scripts': [
              'vaillant=vaillant.__main__:main',
          ]
      },
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Home Automation'
      ]
      )
