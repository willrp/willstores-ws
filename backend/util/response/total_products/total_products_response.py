from flask_restplus import fields

from .total_products_schema import TotalProductsSchema


class TotalProductsResponse(object):
    @staticmethod
    def get_model(api, name):
        return api.model(
            name,
            {
                "count": fields.Integer
            }
        )

    @staticmethod
    def marshall_json(data_out):
        schema = TotalProductsSchema()
        jsonsend = schema.load(data_out)
        return jsonsend
