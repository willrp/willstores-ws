from flask_restplus import fields

from ..models.price import PriceResponse
from .product_total_schema import ProductTotalSchema


class ProductTotalResponse(object):
    @staticmethod
    def get_model(api, name):
        return api.model(
            name,
            {
                "total": fields.Nested(PriceResponse.get_model(api, "PriceOut"))
            }
        )

    @staticmethod
    def marshall_json(data_out):
        schema = ProductTotalSchema()
        jsonsend = schema.load(data_out)
        return jsonsend
