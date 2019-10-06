from flask_restplus import Namespace, Resource

from backend.service import ProductService
from backend.util.response.product_results import ProductResultsResponse
from backend.util.response.error import ErrorResponse
from backend.controller import ErrorHandler, auth_required


productNS = Namespace("Product", description="Product related operations.")

RESPONSEMODEL = ProductResultsResponse.get_model(productNS, "ProductResultsResponse")
ERRORMODEL = ErrorResponse.get_model(productNS, "ErrorResponse")


@productNS.route("/<string:productid>", strict_slashes=False)
class ProductController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__productservice = ProductService()

    @auth_required()
    @productNS.doc(security=["token"])
    @productNS.param("productid", description="The desired product ID", _in="path", required=True)
    @productNS.response(200, "Success", RESPONSEMODEL)
    @productNS.response(401, "Unauthorized", ERRORMODEL)
    @productNS.response(404, "Not Found", {})
    @productNS.response(500, "Unexpected Error", ERRORMODEL)
    @productNS.response(504, "Error while accessing the gateway server", ERRORMODEL)
    def get(self, productid):
        """Product information."""
        try:
            product = self.__productservice.select_by_id(productid)
            jsonsend = ProductResultsResponse.marshall_json(product.get_dict())
            return jsonsend
        except Exception as error:
            return ErrorHandler(error).handle_error()
