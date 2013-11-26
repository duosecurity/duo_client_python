from distutils.core import setup

from duo_client import __version__

setup(
    name='duo_client',
    version=__version__,
    description='Reference client for Duo Security APIs',
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
)
