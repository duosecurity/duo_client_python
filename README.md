# Overview

**Auth** - https://www.duosecurity.com/docs/authapi

**Verify** - https://www.duosecurity.com/docs/duoverify

**Admin** - https://www.duosecurity.com/docs/adminapi

**Accounts** - https://www.duosecurity.com/docs/accountsapi

# Installing

Development:

```
$ git clone https://github.com/duosecurity/duo_client_python.git
$ cd duo_client_python
$ pip install --requirement requirements.txt
$ pip install --requirement requirements-dev.txt
```

System:

```
$ pip install duo_client
```

# Using

See the `examples` folder for how to use this library.

# Testing

```
$ nose2
```

# Linting

```
$ flake8 --ignore=E501 duo_client/ tests/
```
