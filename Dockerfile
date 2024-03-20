FROM python:3.11.6-slim

RUN apt-get update

# install git without interaction
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -yq install git

RUN mkdir /app

WORKDIR /app

COPY ./pyproject.toml /app/

RUN pip install poetry

# PROD
# RUN poetry config virtualenvs.create false \
#     && poetry install --no-dev --no-interaction --no-ansi --no-root
# DEV
RUN apt-get update && apt-get install -y r-base
RUN apt-get update && apt-get install -y graphviz

RUN apt-get update && \
    apt-get install -y \
        libcurl4-openssl-dev \
        libssl-dev \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y libxml2-dev
RUN apt-get update && apt-get install -y libglpk-dev

# installing the necessary package for the process animation
# takes more than 30min to install all the dependencies
RUN R -e "install.packages(c('curl', 'bupaR', 'dplyr', 'xesreadR', 'processanimateR'), dependencies=TRUE)"


RUN poetry install --no-interaction --no-ansi --no-root -vvv


RUN mkdir src
RUN mkdir temp
RUN mkdir csv


COPY ./src /app/src

# PROD
#CMD ["gunicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000",""]
# DEV
CMD ["poetry","run","uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]