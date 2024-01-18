# Duo Auth API Examples Overview


## Examples

This folder contains various examples to illustrate the usage of the `Auth` module within the 
`duo_client_python` library.  The Duo Auth API is primarily intended for integrating user enrollment
and authentication into a custom third-party application. The expectation is that the third-party
application is providing the necessary user interface and supporting structure to complete primary
authentication for users before calling the Duo Auth API for secure second factor authentication.

These examples use console/tty based interactions to collect necessary information to provide fully
functional interactions with the Duo Auth API.

# Using

To run an example query, execute a command like the following from the repo root:
```python
$ python3 examples/Auth/basic_user_mfa.py
```

Or, from within this folder:
```python
$ python3 basic_user_mfa.py
```

# Tested Against Python Versions
* 3.7
* 3.8
* 3.9
* 3.10
* 3.11
