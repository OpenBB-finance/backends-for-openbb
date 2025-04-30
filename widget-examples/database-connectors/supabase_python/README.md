# Supabase Python

This example will focus on everything that relates with Supabase in order to create a backend in Python for OpenBB Pro. For more information, read our main [README.md](/README.md).

## 1. Get started with Supabase

Check website: https://supabase.com/.

Create an account at https://supabase.com/dashboard/.

## 2. Supabase and Python

Read the [official Supabase connector for python](https://supabase.com/docs/reference/python/introduction).

TL;DR: Install Supabase with `pip install supabase-py`

## 3. Extract Supabase information

![image](https://github.com/OpenBB-finance/backend-for-terminal-pro/assets/25267873/8efa0ac6-2d4d-4e65-b246-08876179c22e)

You will need to identify the following from your Supabase account

```python
supabase: Client = create_client(
    url="XYZ",
    key="XYZ"
)
```

All the information can be found on your project, in Project Settings.

The URL is in the **Project URL** box.

The API key is under **Project API keys**. There are 2 keys available:

- The first is safe to use in a browser if you have enabled Row Level Security for your tables and configured policies.

- The second has the ability to bypass Row Level Security, and should be more secure.
