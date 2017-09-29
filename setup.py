#!/usr/bin/env python
from setuptools import setup

setup(
  name='dorm',
  version='0.2',
  description='Database Object Relational Mapping tool',
  author='Yezy Ilomo',
  author_email='yezileliilomo@hotmail.com',
  packages=['dorm'],
  install_requires=['flask', 'ilo', 'flask-mysql', 'sha3'],
 )
 

