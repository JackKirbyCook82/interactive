# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 2026
@name:   Interactive Brokers Market Objects
@author: Jack Kirby Cook

"""

from collections import OrderedDict as ODict
from collections import namedtuple as ntuple
from datetime import datetime as Datetime

from finance.concepts import Querys, Concepts, OSI
from webscraping.webpages import WebJSONPage
from webscraping.webdatas import WebJSON
from webscraping.weburl import WebURL
from support.mixins import Emptying, Sizing, Partition, Logging

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = []
__copyright__ = "Copyright 2026, Jack Kirby Cook"
__license__ = "MIT License"


Field = ntuple("Field", "name code parser")
market_fields = [Field("last", 31, np.float32), Field("bid", 84, np.float32), Field("ask", 86, np.float32), Field("supply", 85, np.float32), Field("demand", 88, np.float32)]
stock_fields = [Field("ticker", 55, str)] + market_fields
option_fields = [Field("contract", 7219, OSI.parse)] + market_fields
market_parser = lambda mapping: {field.name: field.parser(mapping[field.code]) for field in market_fields}
stock_parser = lambda mapping: {"ticker": str(mapping[55])} | market_parser(mapping)
option_parser = lambda mapping: dict(OSI.parse(mapping[7219])) | market_parser(mapping)
expire_parser = lambda expires: [Datetime.strptime(expire, "%Y%m%d") for expire in expires]
strike_parser = lambda strikes: {Concepts.Securities.Option[key]: list(map(int, strikes)) for key, value in strikes.items()}


class InteractiveMarketURL(WebURL, domain="https://localhost:5000", path=["v1", "api"]): pass
class InteractiveStatusURL(InteractiveMarketURL, path=["iserver", "auth", "status"]): pass
class InteractiveMaintainURL(InteractiveMarketURL, path=["tickle"]): pass
class InteractiveAccountsURL(InteractiveMarketURL, path=["iserver", "accounts"]): pass

class InteractiveSearchURL(InteractiveMarketURL, path=["iserver", "secdef", "search"], parameters={"secType": "STK", "name": True}):
    pass

#    @staticmethod
#    def parameters(*args, product, **kwargs): return {"symbol": str(product.ticker)}

class InteractiveStrikeURL(InteractiveMarketURL, path=["iserver", "secdef", "strikes"], parameters={"secType": "OPT"}):
    pass

#    @staticmethod
#    def parameters(*args, product, expire, **kwargs): return {"symbol": int(product.identity), "month": str(expire.strftime("%b%y").upper())}

class InteractiveSecurityURL(InteractiveMarketURL, path=["iserver", "marketdata", "snapshot"]):
    pass

#    @staticmethod
#    def parameters(*args, products, **kwargs):
#        assert products and all(type(product) is type(products[0]) for product in products)
#        products = list(products) if isinstance(products, list) else [products]
#        identities = ",".join(list(map(lambda product: int(product.identity), products)))
#        if isinstance(products[0], Querys.Symbol): codes = list(map(lambda field: field.code, stock_fields))
#        elif isinstance(products[0], Querys.Contract): codes = list(map(lambda field: field.code, option_fields))
#        else: raise TypeError()
#        return {"conids": identities, "fields": codes}

class InteractiveStockURL(InteractiveSecurityURL): pass
class InteractiveOptionURL(InteractiveSecurityURL): pass


class InteractiveSymbolData(WebJSON, parser=Querys.Symbol, multiple=False, optional=False):
    class Ticker(WebJSON.Text, key="ticker", locator="//1/symbol", parser=str): pass
    class Identity(WebJSON.Text, key="identity", locator="//1/conid", parser=int): pass

class InteractiveExpireData(WebJSON.Text, key="expire", locator="//1/opt", parser=expire_parser, multiple=False, optional=False): pass
class InteractiveStrikeData(WebJSON.Mapping, key="strike", parser=strike_parser, multiple=False, optional=False): pass

class InteractiveSecurityData(WebJSON.Collection, multiple=True, optional=False):
    def execute(self, *args, **kwargs):
        contents = super().execute(*args, **kwargs)
        assert isinstance(contents, list) # <stock_parser> & <option_parser> return {}
        dataframe = pd.DataFrame.from_records(contents)
        return dataframe

class InteractiveStockData(InteractiveSecurityData, key="stock", locator=None, parser=stock_parser):
    def execute(self, *args, **kwargs):
        dataframe = super().execute(*args, **kwargs)
        dataframe["instrument"] = Concepts.Securities.Instrument.STOCK
        dataframe["option"] = Concepts.Securities.Option.EMPTY
        return dataframe

class InteractiveOptionData(InteractiveSecurityData, key="option", locator=None, parser=option_parser):
    def execute(self, *args, **kwargs):
        dataframe = super().execute(*args, **kwargs)
        dataframe["instrument"] = Concepts.Securities.Instrument.OPTION
        return dataframe


class InteractiveStockPage(WebJSONPage):
    pass

#    def execute(self, *args, symbols, **kwargs):
#        url = InteractiveStockURL(*args, products=symbols, **kwargs)
#        self.load(url, *args, **kwargs)
#        datas = InteractiveStockData(self.json, *args, **kwargs)
#        stocks = datas(*args, **kwargs)
#        return stocks

class InteractiveOptionPage(WebJSONPage):
    pass

#    def execute(self, *args, contracts, **kwargs):
#        url = InteractiveOptionURL(*args, products=contracts, **kwargs)
#        self.load(url, *args, **kwargs)
#        datas = InteractiveOptionData(self.json, *args, **kwargs)
#        options = datas(*args, **kwargs)
#        return options

class InteractiveContractPage(WebJSONPage):
    pass

#    def execute(self, *args, symbol, expiry, **kwargs):
#        url = InteractiveSearchURL(*args, product=symbol, **kwargs)
#        self.load(url, *args, **kwargs)
#        data = InteractiveSymbolData(self.json, *args, **kwargs)
#        symbol = data(*args, **kwargs)
#        data = InteractiveExpireData(self.json, *args, **kwargs)
#        expires = data(*args, **kwargs)
#        expires = set(expires) & set(expires)
#        generator = self.generator(*args, symbol=symbol, expires=expires, **kwargs)
#        contracts = list(generator)
#        return contracts

#    def generator(self, *args, symbol, expires, **kwargs):
#        for expire in expires:
#            url = InteractiveStrikeURL(*args, product=symbol, expire=expire, **kwargs)
#            self.load(url, *args, **kwargs)
#            data = InteractiveStrikeData(self.json, *args, **kwargs)
#            strikes = data(*args, **kwargs)
#            for option, strike in strikes.items():
#                contract = dict(ticker=str(symbol.ticker), expiry=expire, option=option, strike=float(strike), identity=int(symbol.identity))
#                contract = Querys.Contract(contract)
#                yield contract


class InteractiveDownloader(Sizing, Emptying, Partition, Logging, ABC, title="Downloaded"): pass
class InteractiveSecurityDownloader(InteractiveDownloader, ABC):
    @staticmethod
    def querys(querys, querytype):
        assert isinstance(querys, (list, dict, querytype))
        assert all([isinstance(query, querytype) for query in querys]) if isinstance(querys, (list, dict)) else True
        if isinstance(querys, querytype): querys = [querys]
        elif isinstance(querys, dict): querys = SODict(querys)
        else: querys = list(querys)
        return querys


class InteractiveStockDownloader(InteractiveSecurityDownloader):
    pass


class InteractiveOptionDownloader(InteractiveSecurityDownloader):
    pass


class InteractiveContractDownloader(InteractiveDownloader):
    pass



