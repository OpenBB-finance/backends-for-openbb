# ElasticSearch Python

This example will focus on everything that relates with ElasticSearch in order to create a backend in Python for OpenBB Pro. For more information, read our main [README.md](/README.md).

## 1. Get started with ElasticSearch

Check website: https://www.elastic.co/.

Create an account at https://cloud.elastic.co/login.

## 2. ElasticSearch and Python

Read the [official ElasticSearch connector for python](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/getting-started-python.html).

TL;DR: Install ElasticSearch with `pip install elasticsearch`

## 3. Extract ElasticSearch information

You will need to identify the following from your ElasticSearch account

```python
client = Elasticsearch(
  "XYZ",
  api_key="XYZ"
)
```

Your Elasticsearch endpoint can be found on the "My deployment" page of your deployment. It will be under Applications, in front of "Elasticsearch" and you can click on "Copy endpoint" directly.

![es-endpoint](https://github.com/OpenBB-finance/backend-for-terminal-pro/assets/25267873/99d5ee6e-ebfa-4823-afa1-39c0edef115e)

For the API key, you can generate it on the "Management" page under Security.

![create-api-key](https://github.com/OpenBB-finance/backend-for-terminal-pro/assets/25267873/e22e8f8c-65f7-4c4e-9e14-0b8a550c9e2b)
