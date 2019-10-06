from flask_restplus import Namespace, Resource

from backend.service import ProductService
from backend.util.request.search_products_request import SearchProductsRequest
from backend.util.response.search_products_results import SearchProductsResultsResponse
from backend.util.response.error import ErrorResponse
from backend.controller import ErrorHandler, auth_required


sessionProductsNS = Namespace("Session", description="Session related operations.")

REQUESTMODEL = SearchProductsRequest.get_model(sessionProductsNS, "SearchProductsRequest")
RESPONSEMODEL = SearchProductsResultsResponse.get_model(sessionProductsNS, "SearchProductsResultsResponse")
ERRORMODEL = ErrorResponse.get_model(sessionProductsNS, "ErrorResponse")


@sessionProductsNS.route("/<string:sessionid>/<int:page>", strict_slashes=False)
class SessionProductsController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__productservice = ProductService()

    @auth_required()
    @sessionProductsNS.doc(security=["token"])
    @sessionProductsNS.param("sessionid", description="The desired session ID", _in="path", required=True)
    @sessionProductsNS.param("page", description="The search page.", _in="path", required=True)
    @sessionProductsNS.param("payload", description="Optional", _in="body", required=False)
    @sessionProductsNS.expect(REQUESTMODEL)
    @sessionProductsNS.response(200, "Success", RESPONSEMODEL)
    @sessionProductsNS.response(204, "No content", ERRORMODEL)
    @sessionProductsNS.response(400, "Bad Request", ERRORMODEL)
    @sessionProductsNS.response(401, "Unauthorized", ERRORMODEL)
    @sessionProductsNS.response(500, "Unexpected Error", ERRORMODEL)
    @sessionProductsNS.response(504, "Error while accessing the gateway server", ERRORMODEL)
    def post(self, sessionid, page):
        """Session products paginated"""
        try:
            in_data = SearchProductsRequest.parse_json()
            products = self.__productservice.select(sessionid=sessionid, page=page, **in_data)

            jsonsend = SearchProductsResultsResponse.marshall_json(
                {
                    "products": [p.get_dict_min() for p in products]
                }
            )
            return jsonsend
        except Exception as error:
            return ErrorHandler(error).handle_error()
