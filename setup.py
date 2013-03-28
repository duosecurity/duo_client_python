from distutils.core import setup

setup(
    name='duo_client',
    version='2.0',
    description='Reference client for Duo Security APIs',
    author='Duo Security, Inc.',
    author_email='support@duosecurity.com',
    url='https://github.com/duosecurity/duo_client_python',
    packages=['duo_client'],
    data_files=[
        ('duo_client', ['duo_client/ca_certs.pem']),
    ],
)
