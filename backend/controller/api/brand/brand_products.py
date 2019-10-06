from flask_restplus import Namespace, Resource

from backend.service import ProductService
from backend.util.request.search_products_request import SearchProductsRequest
from backend.util.response.search_products_results import SearchProductsResultsResponse
from backend.util.response.error import ErrorResponse
from backend.controller import ErrorHandler, auth_required


brandProductsNS = Namespace("Brand", description="Brand related operations.")

REQUESTMODEL = SearchProductsRequest.get_model(brandProductsNS, "SearchProductsRequest")
RESPONSEMODEL = SearchProductsResultsResponse.get_model(brandProductsNS, "SearchProductsResultsResponse")
ERRORMODEL = ErrorResponse.get_model(brandProductsNS, "ErrorResponse")


@brandProductsNS.route("/<string:brand>/<int:page>/", strict_slashes=False)
class BrandProductsController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__productservice = ProductService()

    @auth_required()
    @brandProductsNS.doc(security=["token"])
    @brandProductsNS.param("brand", description="The desired brand", _in="path", required=True)
    @brandProductsNS.param("page", description="The search page.", _in="path", required=True)
    @brandProductsNS.param("payload", description="Optional", _in="body", required=False)
    @brandProductsNS.expect(REQUESTMODEL)
    @brandProductsNS.response(200, "Success", RESPONSEMODEL)
    @brandProductsNS.response(204, "No content", ERRORMODEL)
    @brandProductsNS.response(400, "Bad Request", ERRORMODEL)
    @brandProductsNS.response(401, "Unauthorized", ERRORMODEL)
    @brandProductsNS.response(500, "Unexpected Error", ERRORMODEL)
    @brandProductsNS.response(504, "Error while accessing the gateway server", ERRORMODEL)
    def post(self, brand, page):
        """Brand products paginated"""
        try:
            in_data = SearchProductsRequest.parse_json()
            products = self.__productservice.select(brand=brand, page=page, **in_data)

            jsonsend = SearchProductsResultsResponse.marshall_json(
                {
                    "products": [p.get_dict_min() for p in products]
                }
            )
            return jsonsend
        except Exception as error:
            return ErrorHandler(error).handle_error()
