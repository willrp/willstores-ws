from flask_restplus import Namespace, Resource

from backend.service import ProductService, SessionService
from backend.util.request.search_request import SearchRequest
from backend.util.response.session_results import SessionResultsResponse
from backend.util.response.error import ErrorResponse
from backend.controller import ErrorHandler, auth_required


sessionNS = Namespace("Session", description="Session related operations.")

REQUESTMODEL = SearchRequest.get_model(sessionNS, "SearchRequest")
RESPONSEMODEL = SessionResultsResponse.get_model(sessionNS, "SessionResultsResponse")
ERRORMODEL = ErrorResponse.get_model(sessionNS, "ErrorResponse")


@sessionNS.route("/<string:sessionid>", strict_slashes=False)
class SessionController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__productservice = ProductService()
        self.__sessionservice = SessionService()

    @auth_required()
    @sessionNS.doc(security=["token"])
    @sessionNS.param("sessionid", description="The desired session ID", _in="path", required=True)
    @sessionNS.param("payload", description="Optional", _in="body", required=False)
    @sessionNS.expect(REQUESTMODEL)
    @sessionNS.response(200, "Success", RESPONSEMODEL)
    @sessionNS.response(204, "No products found", ERRORMODEL)
    @sessionNS.response(400, "Bad Request", ERRORMODEL)
    @sessionNS.response(401, "Unauthorized", ERRORMODEL)
    @sessionNS.response(404, "Not Found", {})
    @sessionNS.response(500, "Unexpected Error", ERRORMODEL)
    @sessionNS.response(504, "Error while accessing the gateway server", ERRORMODEL)
    def post(self, sessionid):
        """Session information."""
        try:
            in_data = SearchRequest.parse_json()
            session = self.__sessionservice.select_by_id(sessionid)
            sessions = self.__sessionservice.select(gender=session.gender)
            total = self.__productservice.get_total(sessionid=sessionid, **in_data)
            brands = self.__productservice.select_brands(sessionid=sessionid, **in_data)
            kinds = self.__productservice.select_kinds(sessionid=sessionid, **in_data)
            pricerange = self.__productservice.select_pricerange(sessionid=sessionid)

            jsonsend = SessionResultsResponse.marshall_json(
                {
                    "sessions": sessions,
                    "total": total,
                    "brands": brands,
                    "kinds": kinds,
                    "pricerange": pricerange
                }
            )
            return jsonsend
        except Exception as error:
            return ErrorHandler(error).handle_error()
