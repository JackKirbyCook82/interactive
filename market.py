# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 2026
@name:   Interactive Brokers Market Objects
@author: Jack Kirby Cook

"""

from datetime import datetime as Datetime

from finance.concepts import Querys, Concepts
from webscraping.webpages import WebJSONPage
from webscraping.webdatas import WebJSON
from webscraping.weburl import WebURL
from support.mixins import Emptying, Sizing, Partition, Logging

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = []
__copyright__ = "Copyright 2026, Jack Kirby Cook"
__license__ = "MIT License"


market_fields = {}
market_fields = {str(key): str(value) for key, value in market_fields.items()}
expire_parser = lambda expires: [Datetime.strptime(expire, "%Y%m%d") for expire in expires]
strike_parser = lambda strikes: {Concepts.Securities.Option[key]: list(map(int, strikes)) for key, value in strikes.items()}


class InteractiveMarketURL(WebURL, domain="https://localhost:5000", path=["v1", "api"]): pass
class InteractiveStatusURL(InteractiveMarketURL, path=["iserver", "auth", "status"]): pass
class InteractiveMaintainURL(InteractiveMarketURL, path=["tickle"]): pass
class InteractiveAccountsURL(InteractiveMarketURL, path=["iserver", "accounts"]): pass

class InteractiveSearchURL(InteractiveMarketURL, path=["iserver", "secdef", "search"], parameters={"secType": "STK", "name": True}):
    @staticmethod
    def parameters(*args, product, **kwargs): return {"symbol": str(product.ticker)}

class InteractiveIdentityURL(InteractiveSearchURL): pass
class InteractiveExpiresURL(InteractiveSearchURL): pass

class InteractiveStrikeURL(InteractiveMarketURL, path=["iserver", "secdef", "strikes"], parameters={"secType": "OPT"}):
    @staticmethod
    def parameters(*args, product, expire, **kwargs): return {"symbol": int(product.identity), "month": str(expire.strftime("%b%y").upper())}

class InteractiveSecurityURL(InteractiveMarketURL, path=["iserver", "marketdata", "snapshot"]):
    @staticmethod
    def parameters(*args, products, **kwargs):
        products = list(products) if isinstance(products, list) else [products]
        return {"conids":",".join(list(map(lambda product: int(product.identity), products))), "fields": ",".join(list(map(str, market_fields)))}

class InteractiveStockURL(InteractiveSecurityURL): pass
class InteractiveOptionURL(InteractiveSecurityURL): pass




class InteractiveSymbolData(WebJSON, parser=Querys.Symbol, multiple=False, optional=False):
    class Ticker(WebJSON.Text, key="ticker", locator="//1/symbol", parser=str): pass
    class Identity(WebJSON.Text, key="identity", locator="//1/identity", parser=int): pass

class InteractiveExpireData(WebJSON, key="expire", locator="//1/opt", parser=expire_parser, multiple=False, optional=False): pass
class InteractiveStrikeData(WebJSON.Mapping, key="strike", parser=strike_parser, multiple=False, optional=False): pass




class InteractiveSymbolPage(WebJSONPage):
    def execute(self, *args, **kwargs):
        pass

class InteractiveContractPage(WebJSONPage):
    def execute(self, *args, **kwargs):
        pass




class InteractiveSymbolDownloader(Logging, title="Downloaded"):
    def execute(self, symbols, /, **kwargs):
        pass


class InteractiveContractDownloader(Logging, title="Downloaded"):
    def execute(self, contracts, /, **kwargs):
        pass


class InteractiveStockDownloader(Logging, title="Downloaded"):
    def execute(self, symbols, /, **kwargs):
        pass


class InteractiveOptionDownloader(Logging, title="Downloaded"):
    def execute(self, contracts, /, **kwargs):
        pass



