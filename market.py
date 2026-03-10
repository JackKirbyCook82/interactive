# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 2026
@name:   Interactive Market Objects
@author: Jack Kirby Cook

"""

import itertools
import numpy as np
import pandas as pd
import ib_insync as ibkr
from abc import ABC
from operator import attrgetter
from datetime import datetime as Datetime

from interactive.source import InteractiveDataset
from finance.concepts import Querys, Concepts
from webscraping.webpages import WebATTRPage, WebDownloader
from webscraping.webdatas import WebATTR
from support.concepts import NumRange

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ["InteractiveStockDownloader", "InteractiveOptionDownloader", "InteractiveContractDownloader"]
__copyright__ = "Copyright 2026, Jack Kirby Cook"
__license__ = "MIT License"


ticker_formatter = lambda product: str(product.ticker)
expire_formatter = lambda product: str(product.expire.strftime("%Y%m%d"))
option_formatter = lambda product: str(product.option)[0].upper()
strike_formatter = lambda product: float(product.strike)

ticker_parser = lambda product: str(product[:-15])
expire_parser = lambda product: Datetime.strptime("20" + str(product)[-15:-9], "%Y%m%d")
option_parser = lambda product: {str(option)[0].upper(): option for option in iter(Concepts.Securities.Option) if bool(option)}[str(product)[-9]]
strike_parser = lambda product: float(int(str(product)[-8:]) / 1000)


class InteractiveStocksData(WebATTR, multiple=True, optional=False):
    class Ticker(WebATTR.Text, locator="contract", key="ticker", parser=str): pass
    class Last(WebATTR.Text, locator="last", key="last", parser=np.float32): pass
    class Bid(WebATTR.Text, locator="bid", key="bid", parser=np.float32): pass
    class Ask(WebATTR.Text, locator="ask", key="ask", parser=np.float32): pass
    class Demand(WebATTR.Text, locator="bidSize", key="demand", parser=np.int32): pass
    class Supply(WebATTR.Text, locator="askSize", key="supply", parser=np.int32): pass

    def execute(self, *args, **kwargs):
        stock = super().execute(*args, **kwargs)
        assert isinstance(stock, dict)
        stock = pd.DataFrame.from_records([stock])
        stock["instrument"] = Concepts.Securities.Instrument.STOCK
        stock["option"] = Concepts.Securities.Option.EMPTY
        return stock


class InteractiveOptionsData(WebATTR, ABC, multiple=False, optional=False):
    class Ticker(WebATTR.Text, locator="contract", key="ticker", parser=ticker_parser): pass
    class Expire(WebATTR.Text, locator="contract", key="expire", parser=expire_parser): pass
    class Strike(WebATTR.Text, locator="contract", key="strike", parser=strike_parser): pass
    class Option(WebATTR.Text, locator="contract", key="option", parser=option_parser): pass
    class Last(WebATTR.Text, locator="last", key="last", parser=np.float32): pass
    class Bid(WebATTR.Text, locator="bid", key="bid", parser=np.float32): pass
    class Ask(WebATTR.Text, locator="ask", key="ask", parser=np.float32): pass
    class Demand(WebATTR.Text, locator="bidSize", key="demand", parser=np.int32): pass
    class Supply(WebATTR.Text, locator="askSize", key="supply", parser=np.int32): pass
    class Implied(WebATTR.Text, locator="modelGreeks.impliedVol", key="implied", parser=np.float32): pass

    def execute(self, *args, **kwargs):
        option = super().execute(*args, **kwargs)
        assert isinstance(option, dict)
        option = pd.DataFrame.from_records([option])
        option["instrument"] = Concepts.Securities.Instrument.OPTION
        return option


class InteractiveStockPage(WebATTRPage):
    def execute(self, *args, symbols, **kwargs):
        products = [ibkr.Stock(ticker_formatter(symbol), "SMART", "USD") for symbol in symbols]
        stocks = self.load(InteractiveDataset.STOCKS, *args, products=products, **kwargs)
        stocks = [stock(*args, **kwargs) for stock in iter(stocks)]
        stocks = pd.concat(stocks, axis=0)
        return stocks

class InteractiveOptionPage(WebATTRPage):
    def execute(self, *args, contracts, **kwargs):
        products = [ibkr.Option(ticker_formatter(contract), expire_formatter(contract), strike_formatter(contract), option_formatter(contract), "SMART") for contract in contracts]
        options = self.load(InteractiveDataset.OPTIONS, *args, products=products, **kwargs)
        options = [option(*args, **kwargs) for option in iter(options)]
        options = pd.concat(options, axis=0)
        return options

class InteractiveContractPage(WebATTRPage):
    def execute(self, *args, symbol, expiry=None, strikes=None, **kwargs):
        underlying = ibkr.Stock(ticker_formatter(symbol), "SMART", "USD")
        underlying = self.load(InteractiveDataset.STOCKS, *args, products=[underlying], **kwargs)[0]
        chain = self.load(InteractiveDataset.CHAINS, *args, products=[underlying], **kwargs)[0]
        strikes = NumRange([underlying.last * strike for strike in strikes]) if strikes is not None else strikes
        isin = lambda value, values: value in values if values is not None else True
        expires = [expire for expire in sorted(chain.expirations) if isin(expire, expiry)]
        strikes = [strike for strike in sorted(chain.strikes) if isin(strike, strikes)]
        options = {"P": Concepts.Securities.Option.PUT, "C": Concepts.Securities.Option.CALL}
        products = itertools.product([underlying.ticker], expires, strikes, list(options.keys()))
        products = [ibkr.Option(*product, "SMART") for product in products]
        contracts = self.load(InteractiveDataset.CONTRACTS, *args, products=products, **kwargs)
        ticker = lambda contract: str(contract)
        expire = lambda contract: Datetime.strptime(contract.lastTradeDateOrContractMonth, "%Y%m%d")
        option = lambda contract: options[contract.right]
        strike = lambda contract: float(contract.strike)
        contracts = [Querys.Contract(ticker(contract), expire(contract), option(contract), strike(contracts)) for contract in iter(contracts)]
        return contracts


class InteractiveSecurityDownloader(WebDownloader, ABC):
    def download(self, /, **kwargs):
        securities = self.page(**kwargs)
        assert isinstance(securities, pd.DataFrame)
        assert not self.empty(securities)
        return securities


class InteractiveStockDownloader(InteractiveSecurityDownloader, page=InteractiveStockPage):
    def execute(self, symbols, /, **kwargs):
        symbols = self.querys(symbols, Querys.Symbol)
        if not bool(symbols): return
        symbols = [symbols[index:index+25] for index in range(0, len(symbols), 25)]
        for symbols in iter(symbols):
            stocks = self.download(symbols=symbols, **kwargs)
            assert isinstance(stocks, pd.DataFrame)
            if self.empty(stocks): continue
            if isinstance(symbols, dict):
                function = lambda series: symbols[Querys.Symbol(series.to_dict())]
                values = stocks[list(Querys.Symbol)].apply(function, axis=1, result_type="expand")
                stocks = pd.concat([stocks, values], axis=1)
            symbols = self.keys(stocks, by=Querys.Symbol)
            symbols = ",".join(list(map(str, symbols)))
            size = self.size(stocks)
            self.console(f"{str(symbols)}[{int(size):.0f}]")
            if self.empty(stocks): continue
            yield stocks


class InteractiveOptionDownloader(InteractiveSecurityDownloader, page=InteractiveOptionPage):
    def execute(self, contracts, /, **kwargs):
        contracts = self.querys(contracts, Querys.Contract)
        if not bool(contracts): return
        sortkey = attrgetter("ticker", "expire")
        contracts = [list(group) for _, group in itertools.groupby(sorted(contracts, key=sortkey), key=sortkey)]
        for contracts in iter(contracts):
            options = self.download(contracts=contracts, **kwargs)
            assert isinstance(options, pd.DataFrame)
            if self.empty(options): continue
            if isinstance(contracts, dict):
                function = lambda series: contracts[Querys.Contract(series.to_dict())]
                values = options[list(Querys.Contract)].apply(function, axis=1, result_type="expand")
                options = pd.concat([options, values], axis=1)
            settlements = self.keys(options, by=Querys.Settlement)
            settlements = ",".join(list(map(str, settlements)))
            size = self.size(options)
            self.console(f"{str(settlements)}[{int(size):.0f}]")
            if self.empty(options): continue
            yield options


class InteractiveContractDownloader(InteractiveSecurityDownloader, page=InteractiveContractPage):
    def execute(self, symbols, /, expiry=None, **kwargs):
        symbols = self.querys(symbols, Querys.Symbol)
        if not bool(symbols): return
        for symbol in iter(symbols):
            contracts = self.download(symbol=symbol, expiry=expiry, **kwargs)
            self.console(f"{str(symbol)}[{len(contracts):.0f}]")
            if not bool(contracts): continue
            yield contracts

    def download(self, /, **kwargs):
        contracts = self.page(**kwargs)
        assert isinstance(contracts, list)
        contracts.sort(key=lambda contract: contract.expire)
        return contracts



