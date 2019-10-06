from flask_restplus import Namespace, Resource

from backend.service import ProductService
from backend.util.request.product_list_request import ProductListRequest
from backend.util.response.search_products_results import SearchProductsResultsResponse
from backend.util.response.error import ErrorResponse
from backend.controller import ErrorHandler, auth_required


productListNS = Namespace("Product", description="Product related operations.")

REQUESTMODEL = ProductListRequest.get_model(productListNS, "ProductListRequest")
RESPONSEMODEL = SearchProductsResultsResponse.get_model(productListNS, "SearchProductsResultsResponse")
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
    @productListNS.response(401, "Unauthorized", ERRORMODEL)
    @productListNS.response(500, "Unexpected Error", ERRORMODEL)
    @productListNS.response(504, "Error while accessing the gateway server", ERRORMODEL)
    def post(self):
        """Product information list."""
        try:
            in_data = ProductListRequest.parse_json()
            products = self.__productservice.select_by_id_list(**in_data)
            jsonsend = SearchProductsResultsResponse.marshall_json(
                {
                    "products": [p.get_dict_min() for p in products]
                }
            )
            return jsonsend
        except Exception as error:
            return ErrorHandler(error).handle_error()
