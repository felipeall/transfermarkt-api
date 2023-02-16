ARG FROM_CONTAINER_NAME=public.ecr.aws/docker/library/python
FROM --platform=linux/amd64 ${FROM_CONTAINER_NAME}:${PYTHON_RELEASE:-3.9.16}-slim-buster

WORKDIR /opt

COPY poetry.lock pyproject.toml ./

RUN pip3 install --upgrade pip \
    && pip3 install poetry \
    && poetry config virtualenvs.create false \
    && poetry install

COPY ./app /opt/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]