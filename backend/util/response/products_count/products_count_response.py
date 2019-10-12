from flask_restplus import fields

from .products_count_schema import ProductsCountSchema


class ProductsCountResponse(object):
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
        schema = ProductsCountSchema()
        jsonsend = schema.load(data_out)
        return jsonsend
