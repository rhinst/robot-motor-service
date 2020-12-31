from setuptools import setup, find_packages
import platform


setup(
  name='robot-motor-service',
  version='0.1',
  description='Robot motor service',
  url='https://github.com/rhinst/robot-motor-service',
  author='Rob Hinst',
  author_email='rob@hinst.net',
  license='MIT',
  packages=find_packages(),
  data_files = [
    ('config', ['config/default.yaml']),
    ('config/dev', ['config/dev/env.yaml.dist']),
  ],
  install_requires = [
    'redis==3.5.3',
    'himl==0.7.0',
    'RPi.GPIO==0.7.0' if platform.platform().lower().find("armv71") > -1 else 'Mock.GPIO==0.1.7',
  ],
  test_suite='tests',
  tests_require=['pytest==6.2.1'],
  entry_points={
    'console_scripts': ['motor=motor.__main__:main']
  }
)