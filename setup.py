from setuptools import setup, find_packages

setup(name='vr900-connector',
      version='0.0.26',
      description='Connector to handle vaillant vr900/vr920 data',
      long_description='Connector to handle vaillant vr900/vr920 data',
      url='https://github.com/thomasgermain/vr900-connector.git',
      author='Thomas Germain',
      author_email='thomas.germain@live.be',
      license='MIT',
      packages=find_packages(exclude=('tests', 'tests/*', '/tests', '/tests/*')),
      zip_safe=False,
      setup_requires=["pytest-runner"],
      install_requires=["requests", "responses", "pytest"])
