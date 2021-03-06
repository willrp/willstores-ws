from flask_restplus import Namespace, Resource

from backend.service import ProductService
from backend.util.response.products_count import ProductsCountResponse
from backend.util.response.error import ErrorResponse
from backend.controller import ErrorHandler, auth_required


startNS = Namespace("Start", description="Initial operations.")

RESPONSEMODEL = ProductsCountResponse.get_model(startNS, "ProductsCountResponse")
ERRORMODEL = ErrorResponse.get_model(startNS, "ErrorResponse")


@startNS.route("", strict_slashes=False)
class StartController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__productservice = ProductService()

    @auth_required()
    @startNS.doc(security=["token"])
    @startNS.response(200, "Success", RESPONSEMODEL)
    @startNS.response(401, "Unauthorized", ERRORMODEL)
    @startNS.response(500, "Unexpected Error", ERRORMODEL)
    @startNS.response(504, "Error while accessing the gateway server", ERRORMODEL)
    def get(self):
        """Total products registered."""
        try:
            numproducts = self.__productservice.products_count()
            jsonsend = ProductsCountResponse.marshall_json({"count": numproducts})
            return jsonsend
        except Exception as error:
            return ErrorHandler(error).handle_error()
