from flask import request
from flask_restplus import fields

from .product_list_schema import ProductListSchema


class ProductListRequest(object):
    @staticmethod
    def get_model(api, name):
        return api.model(
            name,
            {
                "id_list": fields.List(fields.String(required=True, description="Product ID list"), required=True)
            }
        )

    @staticmethod
    def parse_json():
        jsonrecv = request.get_json()
        schema = ProductListSchema()
        in_data = schema.load(jsonrecv)
        return in_data
