FROM python:3.10-slim

ARG YOUR_ENV
ENV YOUR_ENV=${YOUR_ENV} \
    POETRY_VERSION=1.5.1

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN pip install "poetry==$POETRY_VERSION"

RUN poetry config virtualenvs.create false
RUN poetry install

COPY . .

CMD ["gunicorn", "config.wsgi:application", "--bind", "0:8000" ]