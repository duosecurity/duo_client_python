from __future__ import absolute_import
from setuptools import setup

import os.path

import duo_client

requirements_filename = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')

with open(requirements_filename) as fd:
    install_requires = [i.strip() for i in fd.readlines()]

requirements_dev_filename = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'requirements-dev.txt')

with open(requirements_dev_filename) as fd:
    tests_require = [i.strip() for i in fd.readlines()]

long_description_filename = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'README.md')

with open(long_description_filename) as fd:
    long_description = fd.read()

setup(
    name='duo_client',
    version=duo_client.__version__,
    description='Reference client for Duo Security APIs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Duo Security, Inc.',
    author_email='support@duosecurity.com',
    url='https://github.com/duosecurity/duo_client_python',
    packages=['duo_client'],
    package_data={'duo_client': ['ca_certs.pem']},
    license='BSD',
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
    ],
    install_requires=install_requires,
    tests_require=tests_require,
)
