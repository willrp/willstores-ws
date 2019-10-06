from marshmallow import Schema, fields


class TotalProductsSchema(Schema):
    count = fields.Integer(required=True)
