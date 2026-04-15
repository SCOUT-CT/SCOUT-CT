# From official documentation
ARG PYTHON_BASE=3.12-slim
# build stage
FROM python:$PYTHON_BASE AS builder
LABEL org.opencontainers.image.source=https://github.com/ya-cttool/atlas-proto1

# install PDM
RUN pip install -U pdm
# disable update check
ENV PDM_CHECK_UPDATE=false
# copy files
# COPY pyproject.toml pdm.lock /project/
# COPY src/ /project/src
# COPY test/ /project/test
# COPY config/ /project/config

# # install dependencies and project into the local packages directory
# WORKDIR /project

# RUN mkdir results
# RUN pdm install --check --prod --no-editable
