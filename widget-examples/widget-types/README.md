# Widget Examples

This utilizes data from <https://api.llama.fi/v2/chain> and other sources to render widgets inside an OpenBB dashboard.

For more examples on what you can pass and setting up your own backend - you can head to our documentation at <https://docs.openbb.co/pro>.

These examples include:

- [Table Widget](/table_widget)
- [Chart Widget](/chart_widget)
- [Markdown Widget](/markdown_widget)
- [Metric Widget](/metric_widget)

To Run the backend

```python
pip install -r requirements.txt
```

cd into the Example folder you want to run

```python
Run `uvicorn main:app --port 5050`
```

## Step 3 - Add to Pro

Now you can add the backend to the [data connectors page](https://pro.openbb.co/app/data-connectors) with the base url of your API. In this case it is `http://localhost:5050`
