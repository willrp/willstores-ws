from flask_restplus import Namespace, Resource

from backend.service import ProductService, SessionService
from backend.util.request.gender_request import GenderRequest
from backend.util.response.gender_results import GenderResultsResponse
from backend.util.response.error import ErrorResponse
from backend.controller import ErrorHandler, auth_required


genderNS = Namespace("Gender", description="Gender related operations.")

REQUESTMODEL = GenderRequest.get_model(genderNS, "GenderRequest")
RESPONSEMODEL = GenderResultsResponse.get_model(genderNS, "GenderResultsResponse")
ERRORMODEL = ErrorResponse.get_model(genderNS, "ErrorResponse")


@genderNS.route("/<string:gender>", strict_slashes=False)
class GenderController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__productservice = ProductService()
        self.__sessionservice = SessionService()

    @auth_required()
    @genderNS.doc(security=["token"])
    @genderNS.param("gender", description="The desired gender", _in="path", required=True)
    @genderNS.param("payload", description="Optional", _in="body", required=False)
    @genderNS.expect(REQUESTMODEL)
    @genderNS.response(200, "Success", RESPONSEMODEL)
    @genderNS.response(204, "No Content", {})
    @genderNS.response(400, "Bad Request", ERRORMODEL)
    @genderNS.response(401, "Unauthorized", ERRORMODEL)
    @genderNS.response(500, "Unexpected Error", ERRORMODEL)
    @genderNS.response(504, "Error while accessing the gateway server", ERRORMODEL)
    def post(self, gender="Men"):
        """Gender information."""
        try:
            in_data = GenderRequest.parse_json()
            discounts = self.__productservice.super_discounts(gender=gender, **in_data)
            sessions = self.__sessionservice.select(gender=gender)
            brands = self.__productservice.select_brands(gender=gender)
            kinds = self.__productservice.select_kinds(gender=gender)

            jsonsend = GenderResultsResponse.marshall_json(
                {
                    "discounts": [d.get_dict_min() for d in discounts],
                    "sessions": sessions,
                    "brands": brands,
                    "kinds": kinds
                }
            )
            return jsonsend
        except Exception as error:
            return ErrorHandler(error).handle_error()
