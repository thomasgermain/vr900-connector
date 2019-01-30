from setuptools import setup

setup(name='vr900-connector',
      version='0.0.17',
      description='Connector to handle vaillant vr900/vr920 data',
      long_description='Connector to handle vaillant vr900/vr920 data',
      url='https://github.com/thomasgermain/vr900-connector.git',
      author='Thomas Germain',
      author_email='thomas.germain@live.be',
      license='MIT',
      packages=['vr900connector'],
      zip_safe=False,
      setup_requires=["pytest-runner"],
      install_requires=["requests", "responses", "pytest"])
