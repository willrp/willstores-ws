from flask_restplus import Namespace, Resource

from backend.service import ProductService
from backend.util.request.search_request import SearchRequest
from backend.util.response.search_results import SearchResultsResponse
from backend.util.response.error import ErrorResponse
from backend.controller import ErrorHandler, auth_required


brandNS = Namespace("Brand", description="Brand related operations.")

REQUESTMODEL = SearchRequest.get_model(brandNS, "SearchRequest")
RESPONSEMODEL = SearchResultsResponse.get_model(brandNS, "SearchResultsResponse")
ERRORMODEL = ErrorResponse.get_model(brandNS, "ErrorResponse")


@brandNS.route("/<string:brand>/", strict_slashes=False)
class BrandController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__productservice = ProductService()

    @auth_required()
    @brandNS.doc(security=["token"])
    @brandNS.param("brand", description="The desired brand", _in="path", required=True)
    @brandNS.param("payload", description="Optional", _in="body", required=False)
    @brandNS.expect(REQUESTMODEL)
    @brandNS.response(200, "Success", RESPONSEMODEL)
    @brandNS.response(204, "No Content", ERRORMODEL)
    @brandNS.response(400, "Bad Request", ERRORMODEL)
    @brandNS.response(401, "Unauthorized", ERRORMODEL)
    @brandNS.response(500, "Unexpected Error", ERRORMODEL)
    @brandNS.response(504, "Error while accessing the gateway server", ERRORMODEL)
    def post(self, brand):
        """Brand information."""
        try:
            in_data = SearchRequest.parse_json()
            total = self.__productservice.get_total(brand=brand, **in_data)
            brands = self.__productservice.select_brands(brand=brand, **in_data)
            kinds = self.__productservice.select_kinds(brand=brand, **in_data)

            if "pricerange" in in_data:
                pricerange = in_data["pricerange"]
            else:
                pricerange = self.__productservice.select_pricerange(brand=brand)

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
