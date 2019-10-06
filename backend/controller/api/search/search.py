from flask_restplus import Namespace, Resource

from backend.service import ProductService
from backend.util.request.search_request import SearchRequest
from backend.util.response.search_results import SearchResultsResponse
from backend.util.response.error import ErrorResponse
from backend.controller import ErrorHandler, auth_required


searchNS = Namespace("Search", description="Search related operations.")

REQUESTMODEL = SearchRequest.get_model(searchNS, "SearchRequest")
RESPONSEMODEL = SearchResultsResponse.get_model(searchNS, "SearchResultsResponse")
ERRORMODEL = ErrorResponse.get_model(searchNS, "ErrorResponse")


@searchNS.route("/<string:query>", strict_slashes=False)
class SearchController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__productservice = ProductService()

    @auth_required()
    @searchNS.doc(security=["token"])
    @searchNS.param("query", description="The search query", _in="path", required=True)
    @searchNS.param("payload", description="Optional", _in="body", required=False)
    @searchNS.expect(REQUESTMODEL)
    @searchNS.response(200, "Success", RESPONSEMODEL)
    @searchNS.response(204, "No Content", ERRORMODEL)
    @searchNS.response(400, "Bad Request", ERRORMODEL)
    @searchNS.response(401, "Unauthorized", ERRORMODEL)
    @searchNS.response(500, "Unexpected Error", ERRORMODEL)
    @searchNS.response(504, "Error while accessing the gateway server", ERRORMODEL)
    def post(self, query):
        """Search information."""
        try:
            in_data = SearchRequest.parse_json()
            total = self.__productservice.get_total(query=query, **in_data)
            brands = self.__productservice.select_brands(query=query, **in_data)
            kinds = self.__productservice.select_kinds(query=query, **in_data)

            if "pricerange" in in_data:
                pricerange = in_data["pricerange"]
            else:
                pricerange = self.__productservice.select_pricerange(query=query)

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
