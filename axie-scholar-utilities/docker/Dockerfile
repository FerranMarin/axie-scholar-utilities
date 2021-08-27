FROM python:3.8-alpine as python-base
# We need gcc and libc-dev
RUN apk add --no-cache gcc libc-dev

COPY /docker/get-poetry.py /opt/app/
COPY /source/ /opt/app/

WORKDIR /opt/app/
# Install Poetry
RUN python get-poetry.py --version 1.1.5 && rm get-poetry.py
ENV PATH="/root/.poetry/bin:${PATH}"

FROM python-base as production
# Install depenencies
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT ["python", "axie_scholar_cli.py"]

FROM python-base as tests
# Install depenencies
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

ENTRYPOINT ["poetry", "run", "pytest"]