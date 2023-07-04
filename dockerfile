FROM python:3.11-slim

RUN mkdir /app

WORKDIR /app

COPY ./pyproject.toml /app/

RUN pip install poetry

# PROD
# RUN poetry config virtualenvs.create false \
#     && poetry install --no-dev --no-interaction --no-ansi --no-root
# DEV
RUN poetry install --no-interaction --no-ansi --no-root

RUN mkdir src
RUN mkdir temp
RUN mkdir csv

COPY ./src /app/src

# PROD
#CMD ["gunicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
# DEV
CMD ["poetry","run","uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]