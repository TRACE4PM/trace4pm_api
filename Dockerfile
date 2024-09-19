FROM python:3.11.6-slim

# If you need to run the app using an ARM Mac, this is related to cvxopt library not compiling with aarch64 architecture
# FROM --platform=linux/amd64 python:3.11.6-slim

RUN apt-get update

# install git without interaction
ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir /app
WORKDIR /app

COPY ./pyproject.toml /app/

RUN pip install poetry

#RUN apt-get update && apt-get install -y r-base
#RUN apt-get update && apt-get install -y graphviz
#RUN apt-get -yq install git


RUN apt-get update && \
    apt-get install -y \
        libcurl4-openssl-dev \
        libssl-dev \
        r-base \
        graphviz \
        git \
        libxml2-dev \
        libglpk-dev \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

#RUN apt-get update && apt-get install -y libxml2-dev
#RUN apt-get update && apt-get install -y libglpk-dev

# installing the necessary package for the process animation
# takes more than 30min to install all the dependencies
# Please uncomment if you need process animation features
# RUN R -e "install.packages(c('curl', 'bupaR', 'dplyr', 'xesreadR', 'processanimateR', 'anytime'), dependencies=TRUE)"

# Install Python dependencies
RUN poetry install --no-interaction --no-ansi --no-root


# Create required directories
RUN mkdir src
RUN mkdir temp
RUN mkdir temp/logs
RUN mkdir csv

COPY ./src /app/src

# DEV Start cmd
CMD ["poetry","run","uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]