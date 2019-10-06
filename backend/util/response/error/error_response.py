from flask_restplus import fields


class ErrorResponse(object):
    @staticmethod
    def get_model(api, name):
        return api.model(
            name,
            {
                "error": fields.String(required=True)
            }
        )
