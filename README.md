# Overview

[![Build Status](https://github.com/duosecurity/duo_client_python/workflows/Python%20CI/badge.svg)](https://github.com/duosecurity/duo_client_python/actions)
[![Issues](https://img.shields.io/github/issues/duosecurity/duo_client_python)](https://github.com/duosecurity/duo_client_python/issues)
[![Forks](https://img.shields.io/github/forks/duosecurity/duo_client_python)](https://github.com/duosecurity/duo_client_python/network/members)
[![Stars](https://img.shields.io/github/stars/duosecurity/duo_client_python)](https://github.com/duosecurity/duo_client_python/stargazers)
[![License](https://img.shields.io/badge/License-View%20License-orange)](https://github.com/duosecurity/duo_client_python/blob/master/LICENSE)

**Auth** - https://www.duosecurity.com/docs/authapi

**Admin** - https://www.duosecurity.com/docs/adminapi

**Accounts** - https://www.duosecurity.com/docs/accountsapi

**Activity** - The activity endpoint is in public preview and subject to change

## Tested Against Python Versions
* 3.7
* 3.8
* 3.9
* 3.10
* 3.11
* 3.12

## Requirements
Duo_client_python supports Python 3.7 and higher

## TLS 1.2 and 1.3 Support

Duo_client_python uses Python's ssl module and OpenSSL for TLS operations.  Python versions 3.7 (and higher) have both TLS 1.2 and TLS 1.3 support.

# Installing

Development:

```
$ git clone https://github.com/duosecurity/duo_client_python.git
$ cd duo_client_python
$ virtualenv .env
$ source .env/bin/activate
$ pip install --requirement requirements.txt
$ pip install --requirement requirements-dev.txt
$ python setup.py install
```

System:

Install from [PyPi](https://pypi.org/project/duo-client/)
```
$ pip install duo-client
```

# Using

See the `examples` folder for how to use this library.

To run an example query, execute a command like the following from the repo root:
```
$ python examples/Admin/report_users_and_phones.py
```

# Testing

```
$ nose2

Example: `cd tests/admin && nose2`
```

# Linting

```
$ flake8
```
