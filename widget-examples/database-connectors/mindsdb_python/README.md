# MindsDB Python

This example will focus on everything that relates with MindsDB in order to create a backend in Python for OpenBB Pro. For more information, read our main [README.md](/README.md).

## 1. Get started with MindsDB

Check website: https://mindsdb.com/.

Create an account at https://cloud.mindsdb.com/.

## 2. MindsDB and Python

Read the [official MindsDB connector for python](https://mindsdb.com/blog/introduction-to-python-sdk-interact-with-mindsdb-directly-from-python).

TL;DR: Install MindsDB with `pip install mindsdb_sdk`

## 3. Extract MindsDB information

You will need to identify the following from your MindsDB account

```python
server = mindsdb_sdk.connect(
    login='XYZ',
    password='XYZ'
)
```

If you are using MindsDB Cloud account, this is simply your login and password to access your account.

NOTE: If you installed MindsDB locally via pip or Docker, use the connect method with one argument being your IP address and port.

```python
mindsdb_sdk.connect('http://127.0.0.1:47334')
```
