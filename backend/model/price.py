from elasticsearch_dsl import InnerObjectWrapper


class Price(InnerObjectWrapper):
    """
    Price of a Product:
        outlet: Outlet price, discounted
        retail: Retail price, before discount
    """

    @property
    def discount(self) -> float:
        return round((1.0 - (self.outlet / self.retail)) * 100.0, 2)

    def get_dict(self) -> dict:
        return {
            "outlet": format(self.outlet),
            "retail": format(self.retail),
            "symbol": "£"
        }
