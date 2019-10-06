from flask_restplus import Namespace, Resource

from backend.service import ProductService
from backend.util.request.search_products_request import SearchProductsRequest
from backend.util.response.search_products_results import SearchProductsResultsResponse
from backend.util.response.error import ErrorResponse
from backend.controller import ErrorHandler, auth_required


searchProductsNS = Namespace("Search", description="Search related operations.")

REQUESTMODEL = SearchProductsRequest.get_model(searchProductsNS, "SearchProductsRequest")
RESPONSEMODEL = SearchProductsResultsResponse.get_model(searchProductsNS, "SearchProductsResultsResponse")
ERRORMODEL = ErrorResponse.get_model(searchProductsNS, "ErrorResponse")


@searchProductsNS.route("/<string:query>/<int:page>", strict_slashes=False)
class SearchProductsController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__productservice = ProductService()

    @auth_required()
    @searchProductsNS.doc(security=["token"])
    @searchProductsNS.param("query", description="The search query", _in="path", required=True)
    @searchProductsNS.param("page", description="The search page.", _in="path", required=True)
    @searchProductsNS.param("payload", description="Optional", _in="body", required=False)
    @searchProductsNS.expect(REQUESTMODEL)
    @searchProductsNS.response(200, "Success", RESPONSEMODEL)
    @searchProductsNS.response(204, "No content", ERRORMODEL)
    @searchProductsNS.response(400, "Bad Request", ERRORMODEL)
    @searchProductsNS.response(401, "Unauthorized", ERRORMODEL)
    @searchProductsNS.response(500, "Unexpected Error", ERRORMODEL)
    @searchProductsNS.response(504, "Error while accessing the gateway server", ERRORMODEL)
    def post(self, query, page):
        """Search products paginated"""
        try:
            in_data = SearchProductsRequest.parse_json()
            products = self.__productservice.select(query=query, page=page, **in_data)

            jsonsend = SearchProductsResultsResponse.marshall_json(
                {
                    "products": [p.get_dict_min() for p in products]
                }
            )
            return jsonsend
        except Exception as error:
            return ErrorHandler(error).handle_error()
