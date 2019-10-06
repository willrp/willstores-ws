# Willstores WS [![Build Status](https://travis-ci.com/willrp/willstores-ws.svg?branch=master)](https://travis-ci.com/willrp/willstores-ws) [![Coverage Status](https://coveralls.io/repos/github/willrp/willstores-ws/badge.svg?branch=master)](https://coveralls.io/github/willrp/willstores-ws?branch=master)

WillStores is an Web service application, part of the WillBuyer demonstration project. It manages products and sessions information. You can access the API documentation [here](http://willstores.herokuapp.com/api).

This project uses DevOps practices, it's tested on TravisCI, coverage checked by Coveralls and automatically deployed on Heroku. Since it uses free dynos, it might take some seconds for the first access. Thank you for understanding.

## Built With

* [Elasticsearch](https://www.elastic.co): A distributed, RESTful search and analytics engine. To store and search data;
* [Elasticsearch DSL](https://github.com/elastic/elasticsearch-dsl-py): A high-level library to write and run queries against Elasticsearch for Python;
* [Flask](http://flask.pocoo.org): Web applications framework for Python. For managing the routes and web services. For project backend control and model layers;
* [Flask-Restplus](https://github.com/noirbizarre/flask-restplus): An extension for Flask that adds support for quickly building REST APIs expose its documentation properly;
* [Marshmallow](https://github.com/marshmallow-code/marshmallow): A lightweight library for converting complex objects to and from simple Python datatypes. For input JSON payload validation;
* [Python](https://www.python.org): Main backend programming language. For Web services control, service and model layers;
* [Python-dotenv](https://github.com/theskumar/python-dotenv): Get and set values in your .env file in local and production servers;
* [Pip](https://pypi.python.org/pypi/pip): For dependency management of Python APIs, libraries and frameworks. Bundled with Python;
* [Pipenv](https://github.com/pypa/pipenv): Package manager for Python programming language.

## Development tools

* [Click](https://github.com/pallets/click): Python composable command line interface toolkit;
* [Docker](https://www.docker.com/): Performs web services containerization, helping on application development, integration tests and production. Boosts production by getting everything started easily and isolated, and reloading the application on code change.

## Testing tools

* [Coveralls](https://coveralls.io): A hosted analysis tool, providing statistics about your code coverage;
* [Coveralls-python](https://pypi.org/project/coveralls/): Integration between Python and coveralls;
* [Factory Boy](https://github.com/FactoryBoy/factory_boy): A fixtures replacement tool, aiming to replace static, hard to maintain fixtures with easy-to-use factories for complex objects;
* [Pytest](https://github.com/pytest-dev/pytest): A mature full-featured Python testing tool that helps you write better programs;
* [Pytest-cov](https://github.com/pytest-dev/pytest-cov): A plugin to produce coverage reports for Pytest;
* [Pytest-mock](https://github.com/pytest-dev/pytest-mock): Thin-wrapper around the mock package for easier use with Pytest;
* [Requests](https://github.com/requests/requests): For making server HTTP requests;
* [TravisCI](https://travis-ci.com): A hosted continuous integration service used to build and test software projects.

## Production tools

* [Gunicorn](https://gunicorn.org/): A Python WSGI HTTP Server for UNIX;
* [Heroku](https://www.heroku.com/): A platform as a service (PaaS) that enables developers to build, run, and operate applications entirely in the cloud.

## Prerequisites

The following softwares are needed in order to install this application:

* [Python](https://www.python.org) >= 3.7.4;
* [Docker](https://www.docker.com/)
* [Elasticsearch](https://www.elastic.co/) == 5.4.3.

## Package manager - Pipenv

In order to develop different web services and modules, different environments is a must. They will have their own packages, libraries and variables, simulating the production environment. So here, we will use Pipenv to manage everything.

### Installation

To install it, open the command prompt, access the project folder and run:

```
$ pip install pipenv
```

### Install the project dependencies

In order to install all the project dependencies, including the development ones, run the following command:

```
$ pipenv install --dev
```

## Building Docker enviroment and starting the Web service

First of all, one needs a fully functioning [Docker](https://www.docker.com/) installation.

### Building the Web service

After initializing Docker, open the command prompt, go to [root folder](./) and run:

```
$ docker-compose build
```

### Running the Web service

In order to run the application in an isolated Flask development server, run:

```
$ docker-compose up
```

## Accessing the application API

Before this step, make sure that you [the Web service is running](#running-the-web-service).

First, get the IP of you Docker machine. In order to obtain it, open the command prompt and run:

```
$ docker-machine ip
```

The return value of this command will be referenced as DOCKER_MACHINE_IP.

Open your favorite Web browser and type the following in the address/URL bar:

```
http://DOCKER_MACHINE_IP:8000/api
```

## Running tests

Before this step, make sure that you [the Web service is running](#running-the-web-service).

### Testing

In this application, the following tests are made:

* Unit tests;
* Integration tests;
* Functional tests.

In order to test the application with coverage, run the following command:

```
pipenv run test-cov
```

Coverage results will appear after the tests are finished.

### Testing with interactive coverage report on HTML

In order to test the application, with coverage on HTML pages, run the following command:

```
pipenv run test-cov-html
```

Coverage results will appear inside the *cov_html* folder. Open the *index.html* with your favorite browser to see the results.

## Author

Engineered and coded by:
* **Will Roger Pereira** - https://github.com/willrp

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.