# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 2026
@name:   Interactive Brokers Market Objects
@author: Jack Kirby Cook

"""

import numpy as np
import pandas as pd
from abc import ABC
from datetime import datetime as Datetime

from interactive.source import InteractiveDataset
from finance.concepts import Concepts
from webscraping.websupport import WebDownloader
from webscraping.webpages import WebSOCKPage
from webscraping.webdatas import WebNAME

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ["InteractiveStockDownloader", "InteractiveOptionDownloader", "InteractiveContractDownloader"]
__copyright__ = "Copyright 2026, Jack Kirby Cook"
__license__ = "MIT License"


ticker_parser = lambda contract: str(contract[:-15])
expire_parser = lambda contract: Datetime.strptime("20" + str(contract)[-15:-9], "%Y%m%d")
option_parser = lambda contract: {str(option)[0].upper(): option for option in iter(Concepts.Securities.Option) if bool(option)}[str(contract)[-9]]
strike_parser = lambda contract: float(int(str(contract)[-8:]) / 1000)


class InteractiveStocksData(WebNAME, multiple=True, optional=False):
    class Ticker(WebNAME.Text, locator="contract", key="ticker", parser=str): pass
    class Last(WebNAME.Text, locator="last", key="last", parser=np.float32): pass
    class Bid(WebNAME.Text, locator="bid", key="bid", parser=np.float32): pass
    class Ask(WebNAME.Text, locator="ask", key="ask", parser=np.float32): pass
    class Demand(WebNAME.Text, locator="bidSize", key="demand", parser=np.int32): pass
    class Supply(WebNAME.Text, locator="askSize", key="supply", parser=np.int32): pass

    def execute(self, *args, **kwargs):
        stock = super().execute(*args, **kwargs)
        assert isinstance(stock, dict)
        stock = pd.DataFrame.from_records([stock])
        stock["instrument"] = Concepts.Securities.Instrument.STOCK
        stock["option"] = Concepts.Securities.Option.EMPTY
        return stock


class InteractiveOptionsData(WebNAME, ABC, multiple=False, optional=False):
    class Ticker(WebNAME.Text, locator="contract", key="ticker", parser=ticker_parser): pass
    class Expire(WebNAME.Text, locator="contract", key="expire", parser=expire_parser): pass
    class Strike(WebNAME.Text, locator="contract", key="strike", parser=strike_parser): pass
    class Option(WebNAME.Text, locator="contract", key="option", parser=option_parser): pass
    class Last(WebNAME.Text, locator="last", key="last", parser=np.float32): pass
    class Bid(WebNAME.Text, locator="bid", key="bid", parser=np.float32): pass
    class Ask(WebNAME.Text, locator="ask", key="ask", parser=np.float32): pass
    class Demand(WebNAME.Text, locator="bidSize", key="demand", parser=np.int32): pass
    class Supply(WebNAME.Text, locator="askSize", key="supply", parser=np.int32): pass
    class Implied(WebNAME.Text, locator="modelGreeks.impliedVol", key="implied", parser=np.float32): pass

    def execute(self, *args, **kwargs):
        option = super().execute(*args, **kwargs)
        assert isinstance(option, dict)
        option = pd.DataFrame.from_records([option])
        option["instrument"] = Concepts.Securities.Instrument.OPTION
        return option


class InteractivePage(WebSOCKPage, ABC):
    def load(self, dataset, *args, **kwargs):
        self.console(str(dataset), title="Loading")
        return self.source.load(dataset, *args, **kwargs)

class InteractiveStockPage(InteractivePage):
    def execute(self, *args, symbols, **kwargs):
        parameters = dict(symbols=symbols)
        naming = self.load(InteractiveDataset.STOCKS, *args, **parameters, **kwargs)
        datas = InteractiveStocksData(naming, *args, **kwargs)
        stocks = [data(*args, **kwargs) for data in iter(datas)]
        stocks = pd.concat(stocks, axis=0)
        return stocks

class InteractiveContractPage(InteractivePage):
    def execute(self, *args, symbol, expiry, **kwargs):
        parameters = dict(symbol=symbol, expiry=expiry)
        contracts = self.load(InteractiveDataset.OPTIONS, *args, **parameters, **kwargs)
        return contracts

class InteractiveOptionPage(InteractivePage):
    def execute(self, *args, contracts, **kwargs):
        parameters = dict(contracts=contracts)
        naming = self.load(InteractiveDataset.OPTIONS, *args, **parameters, **kwargs)
        datas = InteractiveOptionsData(naming, *args, **kwargs)
        options = [data(*args, **kwargs) for data in iter(datas)]
        options = pd.concat(options, axis=0)
        return options


class InteractiveSecurityDownloader(WebDownloader):
    def download(self, /, **kwargs):
        pass


class InteractiveStockDownloader(InteractiveSecurityDownloader, page=InteractiveStockPage):
    def execute(self, symbols, /, **kwargs):
        pass


class InteractiveOptionDownloader(InteractiveSecurityDownloader, page=InteractiveOptionPage):
    def execute(self, contracts, /, **kwargs):
        pass


class InteractiveContractDownloader(InteractiveSecurityDownloader, page=InteractiveContractPage):
    def execute(self, symbols, /, expiry=None, **kwargs):
        pass

    def download(self, /, **kwargs):
        pass



