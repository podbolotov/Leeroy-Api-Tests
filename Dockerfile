# Первая стадия
FROM python:3.13.1-alpine AS builder

RUN apk update && \
    apk add wget tar

RUN python -m venv /opt/venv

RUN wget https://github.com/allure-framework/allure2/releases/download/2.32.2/allure-2.32.2.tgz && \
    mkdir /opt/allure2 && \
    tar xf ./allure-2.32.2.tgz -C /opt/allure2

ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Вторая стадия
FROM python:3.13.1-alpine
RUN apk update && \
    apk add openjdk21 tzdata

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/allure2 /opt/allure2

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:/opt/allure2/allure-2.32.2/bin:$PATH"

WORKDIR /code

COPY . /code
RUN mkdir /code/allure-results

CMD pytest /code/tests --alluredir=/code/allure-results -s ; \
allure generate /code/allure-results --clean --output /code/allure-report --single-file --name "Leeroy Api Tests" ; \
mv /code/allure-report/index.html /code/allure-report/test-report-$(date +%Y-%m-%d_%H-%M-%S).html
