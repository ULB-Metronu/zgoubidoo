FROM ubuntu:20.04

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        wget \
        build-essential \
        curl \
        git \
        libgl1

RUN wget --no-check-certificate https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

ENV PATH="/root/miniconda3/bin:$PATH"

RUN useradd app \
    && mkdir -p /home/app \
    && chown -v -R app:app /home/app

RUN conda update -n base -c defaults conda
RUN conda create -n py38 python=3.8

ENV PATH /root/miniconda3/envs/py38/bin:$PATH
ENV CONDA_DEFAULT_ENV py38

RUN curl -sSL -k https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python -
ENV PATH="/root/.poetry/bin:$PATH"

WORKDIR /home/app
ENV GIT_SSL_NO_VERIFY=1

RUN git clone --recurse-submodules --branch develop https://github.com/ULB-Metronu/zgoubidoo.git
RUN poetry config virtualenvs.in-project true
WORKDIR /home/app/zgoubidoo
RUN poetry install
WORKDIR /home/app
RUN mkdir reps
WORKDIR /home/app/reps
ENV PATH="/home/app/zgoubidoo/.venv/bin:$PATH"

RUN pip install jupyterlab
