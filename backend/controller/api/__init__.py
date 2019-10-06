from flask import Blueprint
from flask_restplus import Api


bpapi = Blueprint("api", __name__)

authorizations = {
    "token": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

api = Api(bpapi,
    title="WillStores API",
    description="WillStores Web service API - Serving WillBuyer project.",
    version="0.0.1",
    doc="/",
    authorizations=authorizations
)

api.namespaces.clear()

from .start import NSStart

for ns in NSStart:
    api.add_namespace(ns, path="/start")

from .product import NSProduct

for ns in NSProduct:
    api.add_namespace(ns, path="/product")

from .gender import NSGender

for ns in NSGender:
    api.add_namespace(ns, path="/gender")

from .session import NSSession

for ns in NSSession:
    api.add_namespace(ns, path="/session")

from .brand import NSBrand

for ns in NSBrand:
    api.add_namespace(ns, path="/brand")

from .kind import NSKind

for ns in NSKind:
    api.add_namespace(ns, path="/kind")

from .search import NSSearch

for ns in NSSearch:
    api.add_namespace(ns, path="/search")
