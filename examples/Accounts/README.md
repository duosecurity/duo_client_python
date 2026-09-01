# Subaccount Management Examples Overview


## Examples

This folder contains various examples to illustrate the usage of the `Accounts` module within the 
`duo_client_python` library.  Subaccount management in Admin API is primarily intended for use by Managed Service 
Partners (MSP) to assist in the automation of managing their child (customer) Duo accounts.

Subaccount management in Admin API requires special access to be enabled. Please see the 
[online documentation](https://duo.com/docs/adminapi#subaccounts) for more information.

# Using

To run an example query, execute a command like the following from the repo root:
```python
$ python3 examples/Accounts/get_billing_and_telephony_credits.py
```

Or, from within this folder:
```python
$ python3 get_billing_and_telephony_credits.py
```

# Tested Against Python Versions
* 3.7
* 3.8
* 3.9
* 3.10
* 3.11
