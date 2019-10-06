from flask_restplus import Namespace, Resource

from backend.service import ProductService
from backend.util.request.search_products_request import SearchProductsRequest
from backend.util.response.search_products_results import SearchProductsResultsResponse
from backend.util.response.error import ErrorResponse
from backend.controller import ErrorHandler, auth_required


kindProductsNS = Namespace("Kind", description="Kind related operations.")

REQUESTMODEL = SearchProductsRequest.get_model(kindProductsNS, "SearchProductsRequest")
RESPONSEMODEL = SearchProductsResultsResponse.get_model(kindProductsNS, "SearchProductsResultsResponse")
ERRORMODEL = ErrorResponse.get_model(kindProductsNS, "ErrorResponse")


@kindProductsNS.route("/<string:kind>/<int:page>", strict_slashes=False)
class KindProductsController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__productservice = ProductService()

    @auth_required()
    @kindProductsNS.doc(security=["token"])
    @kindProductsNS.param("kind", description="The desired kind", _in="path", required=True)
    @kindProductsNS.param("page", description="The search page.", _in="path", required=True)
    @kindProductsNS.param("payload", description="Optional", _in="body", required=False)
    @kindProductsNS.expect(REQUESTMODEL)
    @kindProductsNS.response(200, "Success", RESPONSEMODEL)
    @kindProductsNS.response(204, "No content", ERRORMODEL)
    @kindProductsNS.response(400, "Bad Request", ERRORMODEL)
    @kindProductsNS.response(401, "Unauthorized", ERRORMODEL)
    @kindProductsNS.response(500, "Unexpected Error", ERRORMODEL)
    @kindProductsNS.response(504, "Error while accessing the gateway server", ERRORMODEL)
    def post(self, kind, page):
        """Kind products paginated"""
        try:
            in_data = SearchProductsRequest.parse_json()
            products = self.__productservice.select(kind=kind, page=page, **in_data)

            jsonsend = SearchProductsResultsResponse.marshall_json(
                {
                    "products": [p.get_dict_min() for p in products]
                }
            )
            return jsonsend
        except Exception as error:
            return ErrorHandler(error).handle_error()
