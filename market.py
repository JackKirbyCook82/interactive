# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 2026
@name:   Interactive Brokers Market Objects
@author: Jack Kirby Cook

"""

from finance.concepts import Concepts
from webscraping.websupport import WebDownloader
from webscraping.webpages import WebJSONPage
from webscraping.webdatas import WebJSON
from support.mixins import Emptying, Sizing, Partition, Logging

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ["InteractiveStockDownloader", "InteractiveOptionDownloader", "InteractiveContractDownloader"]
__copyright__ = "Copyright 2026, Jack Kirby Cook"
__license__ = "MIT License"


class InteractiveStockPage(WebSUBSPage):
    def execute(self, *args, symbols, **kwargs):
        dataset = Concepts.Securities.Instrument.STOCK
        self.load(dataset, *args, symbols=symbols, **kwargs)


class InteractiveContractPage(WebSUBSPage):
    def execute(self, *args, symbol, expiry, **kwargs):
        parameters = dict(symbol=symbol, expiry=expiry, strikes=None)
        contracts = self.source.contracts(*args, **parameters, **kwargs)
        return list(contracts)

class InteractiveOptionPage(WebSUBSPage):
    def execute(self, *args, contracts, **kwargs):
        dataset = Concepts.Securities.Instrument.OPTION
        self.load(datset, *args, contracts=contracts, **kwargs)



class InteractiveSecurityDownloader(WebDownloader):
    def download(self, /, **kwargs):
        pass


class InteractiveStockDownloader(InteractiveSecurityDownloader, page=InteractiveStockPage):
    def execute(self, symbols, /, **kwargs):
        pass


class InteractiveOptionDownloader(InteractiveSecurityDownloader, page=InteractiveOptionPage):
    def execute(self, contracts, /, **kwargs):
        pass


class InteractiveContractDownloader(InteractiveDownloader, page=InteractiveContractPage):
    def execute(self, symbols, /, expiry=None, **kwargs):
        pass

    def download(self, /, **kwargs):
        pass



