# Subaccount Management Examples Overview


## Examples

This folder contains various examples to illustrate the usage of the subaccount management methods of the `Admin`
module within the `duo_client_python` library.  Subaccount management in Admin API is primarily intended for use by
Managed Service Partners (MSP) to assist in the automation of managing their child (customer) Duo accounts.

The child account methods (`get_child_accounts`, `create_account`, `delete_account`) live on `Admin`. The `Accounts`
client also provides them, but it is deprecated and will be removed in a future release, and its copy of these
methods is frozen -- new subaccount API methods are added to `Admin` only. Use `Admin` for new code.

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
