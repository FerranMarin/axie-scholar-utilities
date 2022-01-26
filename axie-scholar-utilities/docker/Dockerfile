FROM python:3.9-alpine as python-base
# External Deps we need
RUN apk add --update --no-cache gcc libc-dev jpeg-dev zlib-dev linux-headers libusb libusb-dev eudev-dev eudev

COPY /docker/get-poetry.py /opt/app/
COPY /source/ /opt/app/

WORKDIR /opt/app/
# Install Poetry
RUN python get-poetry.py --version 1.1.11 && rm get-poetry.py
ENV PATH="/root/.poetry/bin:${PATH}"
# Update PIP
RUN python -m pip install -U pip

FROM python-base as production
# Install depenencies
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT ["python", "axie_scholar_cli.py"]

FROM python-base as production-trezor
# Install depenencies
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT ["python", "trezor_axie_scholar_cli.py"]

FROM python-base as tests
# Install depenencies
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

ENTRYPOINT ["pytest"]