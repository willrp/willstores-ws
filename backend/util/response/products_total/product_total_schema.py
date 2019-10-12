from marshmallow import Schema, fields

from ..models.price import PriceSchema


class ProductTotalSchema(Schema):
    total = fields.Nested(PriceSchema, required=True)
