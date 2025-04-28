{% if cookiecutter.use_docker == 'y' %}
FROM python:{{ cookiecutter.python_version }}-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "{{ cookiecutter.project_slug }}"]
{% endif %} 