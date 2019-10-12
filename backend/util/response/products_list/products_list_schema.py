from marshmallow import Schema, fields

from ..models.product import ProductSchema
from ..models.price import PriceSchema


class ProductsListSchema(Schema):
    products = fields.Nested(ProductSchema, required=True, many=True)
    total = fields.Nested(PriceSchema, required=True)
