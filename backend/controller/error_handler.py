import re

from flask import current_app as app
from flask_restplus import abort
from werkzeug.exceptions import HTTPException, BadRequest
from marshmallow import ValidationError as MarshmallowError
from elasticsearch import ElasticsearchException
from elasticsearch_dsl.exceptions import ElasticsearchDslException

from backend.errors.no_content_error import NoContentError
from backend.errors.request_error import RequestError
from backend.errors.not_found_error import NotFoundError


class ErrorHandler(object):
    def __init__(self, error: Exception):
        self.__error = error

    def handle_error(self):
        errors = {
            NoContentError: self.__handle_NoContentError,
            BadRequest: self.__handle_BadRequestException,
            RequestError: self.__handle_BadRequestException,
            HTTPException: self.__handle_BadRequestException,
            MarshmallowError: self.__handle_MarshmallowError,
            NotFoundError: self.__handle_NotFoundError,
            ElasticsearchException: self.__handle_ElasticsearchException,
            ElasticsearchDslException: self.__handle_ElasticsearchException
        }

        for errtype, errhandler in errors.items():
            if isinstance(self.error, errtype):
                return errhandler()

        return self.__default_handler()

    @property
    def error(self):
        return self.__error

    def __handle_NoContentError(self):
        return {}, 204

    def __handle_BadRequestException(self):
        abort(400, error=str(self.error))

    def __handle_MarshmallowError(self):
        message = re.sub(r'[\{\[\}\]\'}]', "", self.error.messages.__str__())
        abort(400, error=message)

    def __handle_NotFoundError(self):
        return {}, 404

    def __handle_ElasticsearchException(self):
        abort(504, error="Error while accessing the gateway server.")

    def __default_handler(self):
        app.logger.error("UNEXPECTED ERROR: %s" % str(self.error))
        abort(500, error="An unexpected error has occured.")
