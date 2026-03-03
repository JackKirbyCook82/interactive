# -*- coding: utf-8 -*-
"""
Created on Thurs Feb 26 2026
@name:   Interactive Brokers Source Objects
@author: Jack Kirby Cook

"""

import ib_insync as ibkr
from enum import Enum
from itertools import product

from finance.concepts import Concepts, Querys
from webscraping.websupport import WebSource, WebDelayer
from support.concepts import NumRange

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ["InteractiveSource", "InteractiveDataset"]
__copyright__ = "Copyright 2026, Jack Kirby Cook"
__license__ = "MIT License"


InteractiveDataset = Enum("InteractiveDataset", ["STOCKS", "OPTIONS", "CONTRACTS"])


class InteractiveDatasetError(Exception): pass
class InteractiveSource(WebSource):
    def __init__(self, *args, host, port, quoting=Concepts.Markets.Quoting, readonly=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.__readonly = readonly
        self.__quoting = quoting
        self.__host = host
        self.__port = port

    def start(self):
        self.source = ibkr.IB()
        parameters = dict(host=self.host, port=self.port, clientID=self.count, readonly=self.readonly)
        self.source.connect(**parameters)
        quoting = int(self.quoting)
        self.source.reqMarketDataType(quoting)

    def stop(self):
        self.source.disconnect()

    def load(self, dataset, *args, **kwargs):
        if dataset is InteractiveDataset.STOCKS: return self.stocks(*args, **kwargs)
        elif dataset is InteractiveDataset.OPTIONS: return self.options(*args, **kwargs)
        elif dataset is InteractiveDataset.CONTRACTS: return self.contracts(*args, **kwargs)
        else: raise InteractiveDatasetError()

    @WebDelayer.register
    def stocks(self, *args, symbols, **kwargs):
        ticker = lambda symbol: str(symbol.ticker)
        stocks = [ibkr.Stock(ticker(symbol), "SMART", "USD") for symbol in symbols]
        ibkr.qualifyContracts(*stocks)
        return ibkr.reqTickers(*stocks)

    @WebDelayer.register
    def options(self,*args, contracts, **kwargs):
        ticker = lambda contract: str(contract.ticker)
        expire = lambda contract: str(contract.expire.strftime("%Y%m%d"))
        strike = lambda contract: float(contract.strike)
        option = lambda contract: str(contract.option)[0].upper()
        options = [ibkr.Option(ticker(contract), expire(contract), strike(contract), option(contract)) for contract in contracts]
        ibkr.qualifyContracts(*options)
        return ibkr.reqTickers(*options)

    @WebDelayer.register
    def contracts(self, *args, symbol, expiry=None, strikes=None, **kwargs):
        underlying = ibkr.Stock(symbol.ticker, "SMART", "USD")
        underlying = ibkr.qualifyContracts(underlying)
        chain = ibkr.reqSecDefOptParams(underlying.symbol, "", underlying.secType, underlying.conId)
        underlying = ibkr.reqMktData(underlying, snapshot=True)
        ibkr.sleep(1)
        ticker, spot = underlying.symbol, underlying.marketPrice()
        strikes = NumRange([spot * strike for strike in strikes]) if strikes is not None else strikes
        isin = lambda value, values: value in values if values is not None else True
        expires = [expire for expire in sorted(chain.expirations) if isin(expire, expiry)]
        strikes = [strike for strike in sorted(chain.strikes) if isin(strike, strikes)]
        contracts = self.generator([ticker], expires, strikes)
        return contracts

    @staticmethod
    def generator(tickers, expires, strikes):
        for ticker, expire, strike, option in product(tickers, expires, strikes, ["P", "C"]):
            details = ibkr.Option(ticker, expire, strike, option, "SMART")
            details = ibkr.reqContractDetails(details)
            if not bool(details): continue
            assert len(details) == 1
            contract = Querys.Contract(ticker, expire, option, strike, "SMART")
            yield contract

    @property
    def readonly(self): return self.__readonly
    @property
    def quoting(self): return self.__quoting
    @property
    def host(self): return self.__host
    @property
    def port(self): return self.__port

