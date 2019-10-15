from flask_restplus import Namespace, Resource

from backend.service import ProductService
from backend.util.request.product_list_request import ProductListRequest
from backend.util.response.products_total import ProductTotalResponse
from backend.util.response.error import ErrorResponse
from backend.controller import ErrorHandler, auth_required


productTotalNS = Namespace("Product", description="Product related operations.")

REQUESTMODEL = ProductListRequest.get_model(productTotalNS, "ProductListRequest")
RESPONSEMODEL = ProductTotalResponse.get_model(productTotalNS, "ProductTotalResponse")
ERRORMODEL = ErrorResponse.get_model(productTotalNS, "ErrorResponse")


@productTotalNS.route("/total", strict_slashes=False)
class ProductTotalController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__productservice = ProductService()

    @auth_required()
    @productTotalNS.doc(security=["token"])
    @productTotalNS.param("payload", description="Required", _in="body", required=True)
    @productTotalNS.expect(REQUESTMODEL)
    @productTotalNS.response(200, "Success", RESPONSEMODEL)
    @productTotalNS.response(204, "No content", ERRORMODEL)
    @productTotalNS.response(401, "Unauthorized", ERRORMODEL)
    @productTotalNS.response(400, "Bad Request", ERRORMODEL)
    @productTotalNS.response(500, "Unexpected Error", ERRORMODEL)
    @productTotalNS.response(504, "Error while accessing the gateway server", ERRORMODEL)
    def post(self):
        """Product list total price."""
        try:
            in_data = ProductListRequest.parse_json()
            _, total = self.__productservice.select_by_item_list(**in_data)
            jsonsend = ProductTotalResponse.marshall_json(
                {
                    "total": total
                }
            )
            return jsonsend
        except Exception as error:
            return ErrorHandler(error).handle_error()
