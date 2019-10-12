from flask_restplus import Namespace, Resource

from backend.service import ProductService
from backend.util.request.product_list_request import ProductListRequest
from backend.util.response.products_list import ProductsListResponse
from backend.util.response.error import ErrorResponse
from backend.controller import ErrorHandler, auth_required


productListNS = Namespace("Product", description="Product related operations.")

REQUESTMODEL = ProductListRequest.get_model(productListNS, "ProductListRequest")
RESPONSEMODEL = ProductsListResponse.get_model(productListNS, "ProductsListResponse")
ERRORMODEL = ErrorResponse.get_model(productListNS, "ErrorResponse")


@productListNS.route("/list", strict_slashes=False)
class ProductListController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__productservice = ProductService()

    @auth_required()
    @productListNS.doc(security=["token"])
    @productListNS.param("payload", description="Required", _in="body", required=True)
    @productListNS.expect(REQUESTMODEL)
    @productListNS.response(200, "Success", RESPONSEMODEL)
    @productListNS.response(204, "No content", ERRORMODEL)
    @productListNS.response(400, "Bad Request", ERRORMODEL)
    @productListNS.response(401, "Unauthorized", ERRORMODEL)
    @productListNS.response(500, "Unexpected Error", ERRORMODEL)
    @productListNS.response(504, "Error while accessing the gateway server", ERRORMODEL)
    def post(self):
        """Product information list."""
        try:
            in_data = ProductListRequest.parse_json()
            products, total = self.__productservice.select_by_id_list(**in_data)
            jsonsend = ProductsListResponse.marshall_json(
                {
                    "products": [p.get_dict_min() for p in products],
                    "total": total
                }
            )
            return jsonsend
        except Exception as error:
            return ErrorHandler(error).handle_error()
