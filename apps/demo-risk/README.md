![Screenshot 2025-03-31 at 7 41 48 PM](https://github.com/user-attachments/assets/8b2409d6-5ddc-4cbc-b20c-89a29b1bd923)


## Python Installation

Install this in an environment with a version of Python between 3.9-3.12, inclusively.

- Run, `pip install -e .`

- Run, `openbb-api --app demo_risk/app.py --host 0.0.0.0 --port 6020`

- Open the OpenBB Workspace.

- Add `http://127.0.0.1:6020` as a new custom backend.

- Go to the templates page, click Refresh button.

- Click on the new template.

- Enjoy your burrito.

<img width="1783" alt="Screenshot 2025-03-25 at 2 39 06 PM" src="https://github.com/user-attachments/assets/e5e5a454-3123-4644-9820-4d039a0661a3" />


## Docker Installation

To run the application using Docker:

1. Build the Docker image:

```bash
docker build -t demo-risk .
```

2. Run the container:

```bash
docker run -p 6020:6020 demo-risk
```

2. Open the OpenBB Workspace.

3. Add `http://127.0.0.1:6020` as a new custom backend.

4. Go to the templates page, click Refresh button.

5. Click on the new template.

That's it.

## Fly.io Deployment

To deploy the application on Fly.io:

1. Install the Fly.io CLI:

```bash
curl -L https://fly.io/install.sh | sh
```

2. Login to Fly.io:

```bash
fly auth login
```

3. Initialize the app (if not already done):

```bash
fly launch
```

4. Deploy the application:

```bash
fly deploy
```

5. Open the deployed app:

```bash
fly open
```

6. In the OpenBB Workspace:

- Add the deployed URL (e.g., `https://demo-risk.fly.dev`) as a new custom backend.
- Go to the templates page and click Refresh
- Click on the new template

The application is now deployed and accessible from anywhere!

Note: the deployed URL may vary based on your configs.
