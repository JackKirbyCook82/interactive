# -*- coding: utf-8 -*-
"""
Created on Thurs Feb 26 2026
@name:   Interactive Source Objects
@author: Jack Kirby Cook

"""

import ib_insync as ibkr
from enum import Enum

from finance.concepts import Concepts
from webscraping.websupport import WebSource, WebDelayer

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ["InteractiveSource", "InteractiveDataset"]
__copyright__ = "Copyright 2026, Jack Kirby Cook"
__license__ = "MIT License"


InteractiveDataset = Enum("InteractiveDataset", ["STOCKS", "OPTIONS", "CHAINS", "CONTRACTS"])


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

    @WebDelayer.register
    def load(self, dataset, *args, **kwargs):
        if isinstance(dataset, str): dataset = InteractiveDataset[str(dataset).upper()]
        elif dataset in InteractiveDataset: pass
        else: TypeError(type(dataset))
        if dataset is InteractiveDataset.STOCKS: return self.stocks(*args, **kwargs)
        elif dataset is InteractiveDataset.OPTIONS: return self.options(*args, **kwargs)
        elif dataset is InteractiveDataset.CHAINS: return self.chain(*args, **kwargs)
        elif dataset is InteractiveDataset.CONTRACTS: return self.contracts(*args, **kwargs)
        elif dataset is InteractiveDataset.ORDER: return self.order(*args, **kwargs)
        else: raise InteractiveDatasetError()

    @staticmethod
    def stocks(*args, products, **kwargs):
        ibkr.qualifyContracts(*products)
        products = list(ibkr.reqTickers(*products))
        yield from products

    @staticmethod
    def options(*args, products, **kwargs):
        ibkr.qualifyContracts(*products)
        products = list(ibkr.reqTickers(*products))
        yield from products

    @staticmethod
    def chain(*args, products, **kwargs):
        for product in products:
            chain = ibkr.reqSecDefOptParams(product.ticker, "", "STK", product.conId)
            yield chain

    @staticmethod
    def contracts(*args, products, **kwargs):
        for product in products:
            details = ibkr.reqContractDetails(product)
            if not bool(details): continue
            assert len(details) == 1
            yield details[0].contract

    @staticmethod
    def order(*args, order, products, **kwargs):
        ibkr.placeOrder(products, order)

    @property
    def readonly(self): return self.__readonly
    @property
    def quoting(self): return self.__quoting
    @property
    def host(self): return self.__host
    @property
    def port(self): return self.__port

