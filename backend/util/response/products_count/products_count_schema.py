from marshmallow import Schema, fields


class ProductsCountSchema(Schema):
    count = fields.Integer(required=True)
