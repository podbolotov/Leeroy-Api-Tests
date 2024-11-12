# Первая стадия
FROM python:3.12.5-alpine AS builder

RUN apk update && \
    apk add musl-dev libpq-dev gcc wget tar

RUN python -m venv /opt/venv

RUN wget https://github.com/allure-framework/allure2/releases/download/2.30.0/allure-2.30.0.tgz && \
    mkdir /opt/allure2 && \
    tar xf ./allure-2.30.0.tgz -C /opt/allure2

ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Вторая стадия
FROM python:3.12.5-alpine
RUN apk update && \
    apk add libpq-dev && \
    apk add openjdk21

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/allure2 /opt/allure2

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:/opt/allure2/allure-2.30.0/bin:$PATH"

WORKDIR /code

COPY . /code
RUN mkdir /code/allure-results

CMD ["pytest", "/code/tests", "--alluredir=/code/allure-results", "-s", "&&", "allure", "generate", "/code/allure-results", "--clean", "--output", "/code/allure-report", "--single-file", "--name", "Leeroy Api Tests"]
