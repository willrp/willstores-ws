FROM python:3.7-alpine

ENV PIPENV_DONT_LOAD_ENV=1
ENV PIPENV_VERBOSITY=-1
ENV PIPENV_IGNORE_VIRTUALENVS=1

RUN mkdir -p /usr/src
WORKDIR /usr/src

COPY . /usr/src

RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv lock -r > requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install gunicorn

RUN rm backend-test.py backend-dev.py requirements.txt Pipfile Pipfile.lock

CMD ["gunicorn", "-w", "4", "backend:create_app('production')"]