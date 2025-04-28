# ClickHouse Python

This example will focus on everything that relates with ClickHouse in order to create a backend in Python for OpenBB Pro. For more information, read our main [README.md](/README.md).

## 1. Get started with ClickHouse

Check website: https://clickhouse.com/.

Create an account at https://clickhouse.cloud.

## 2. ClickHouse and Python

Read the [official ClickHouse connector for python](https://clickhouse.com/docs/en/integrations/python).

TL;DR: Install ClickHouse with `pip install clickhouse-connect`

## 3. Extract ClickHouse information

<img width="600" alt="Screenshot 2023-10-27 at 12 21 21 AM" src="https://github.com/OpenBB-finance/backend-for-terminal-pro/assets/25267873/6e59755b-577c-4dc9-9975-65b18056efac">

You will need to identify the following from your ClickHouse account

```python
client =  v.get_client(
    host="XYZ",
    port=8443,
    username="default",
    password="XYZ",
)
```

By default, the port and username should be `8443` and `"default"`.

The password is the one associated with your ClickHouse account.

The host can be found by going into ClickHouse Services, then clicking on the **Connect** dropdown and selecting **View connection string**.

<img width="600" alt="Screenshot 2023-10-27 at 12 22 59 AM" src="https://github.com/OpenBB-finance/backend-for-terminal-pro/assets/25267873/6d505791-fd75-402d-8e20-c81067c48303">

There you'll see a **Native** tab with the following

```console
./clickhouse client --host abc123de45.us-east-1.aws.clickhouse.cloud --secure --password
```

where your host will be `abc123de45.us-east-1.aws.clickhouse.cloud`.

<img width="600" alt="Screenshot 2023-10-27 at 12 24 36 AM" src="https://github.com/OpenBB-finance/backend-for-terminal-pro/assets/25267873/451056fd-a5b0-4d60-8991-5ba6d4a1fb14">

