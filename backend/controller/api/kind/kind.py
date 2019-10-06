from flask_restplus import Namespace, Resource

from backend.service import ProductService
from backend.util.request.search_request import SearchRequest
from backend.util.response.search_results import SearchResultsResponse
from backend.util.response.error import ErrorResponse
from backend.controller import ErrorHandler, auth_required


kindNS = Namespace("Kind", description="Kind related operations.")

REQUESTMODEL = SearchRequest.get_model(kindNS, "SearchRequest")
RESPONSEMODEL = SearchResultsResponse.get_model(kindNS, "SearchResultsResponse")
ERRORMODEL = ErrorResponse.get_model(kindNS, "ErrorResponse")


@kindNS.route("/<string:kind>", strict_slashes=False)
class KindController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__productservice = ProductService()

    @auth_required()
    @kindNS.doc(security=["token"])
    @kindNS.param("kind", description="The desired kind", _in="path", required=True)
    @kindNS.param("payload", description="Optional", _in="body", required=False)
    @kindNS.expect(REQUESTMODEL)
    @kindNS.response(200, "Success", RESPONSEMODEL)
    @kindNS.response(204, "No Content", ERRORMODEL)
    @kindNS.response(400, "Bad Request", ERRORMODEL)
    @kindNS.response(401, "Unauthorized", ERRORMODEL)
    @kindNS.response(500, "Unexpected Error", ERRORMODEL)
    @kindNS.response(504, "Error while accessing the gateway server", ERRORMODEL)
    def post(self, kind):
        """Kind information."""
        try:
            in_data = SearchRequest.parse_json()
            total = self.__productservice.get_total(kind=kind, **in_data)
            brands = self.__productservice.select_brands(kind=kind, **in_data)
            kinds = self.__productservice.select_kinds(kind=kind, **in_data)

            if "pricerange" in in_data:
                pricerange = in_data["pricerange"]
            else:
                pricerange = self.__productservice.select_pricerange(kind=kind)

            jsonsend = SearchResultsResponse.marshall_json(
                {
                    "total": total,
                    "brands": brands,
                    "kinds": kinds,
                    "pricerange": pricerange
                }
            )
            return jsonsend
        except Exception as error:
            return ErrorHandler(error).handle_error()
