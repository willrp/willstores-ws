from marshmallow import Schema, fields, validates

from backend.errors.request_error import ValidationError


class ProductListSchema(Schema):
    id_list = fields.List(fields.String(required=True), required=True)

    @validates("id_list")
    def validate_id_list(self, value):
        if not value:
            raise ValidationError("id_list cannot be an empty list.")
