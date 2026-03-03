# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 2026
@name:   Interactive Brokers Market Objects
@author: Jack Kirby Cook

"""

from abc import ABC

from interactive.source import InteractiveDataset
from webscraping.websupport import WebDownloader
from webscraping.webpages import WebPage

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ["InteractiveStockDownloader", "InteractiveOptionDownloader", "InteractiveContractDownloader"]
__copyright__ = "Copyright 2026, Jack Kirby Cook"
__license__ = "MIT License"


class InteractivePage(WebPage, ABC):
    def load(self, dataset, *args, **kwargs):
        self.console(str(dataset), title="Loading")
        return self.source.load(dataset, *args, **kwargs)

class InteractiveStockPage(InteractivePage):
    def execute(self, *args, symbols, **kwargs):
        parameters = dict(symbols=symbols)
        stocks = self.load(InteractiveDataset.STOCKS, *args, **parameters, **kwargs)


class InteractiveContractPage(InteractivePage):
    def execute(self, *args, symbol, expiry, **kwargs):
        parameters = dict(symbol=symbol, expiry=expiry)
        contracts = self.load(InteractiveDataset.OPTIONS, *args, **parameters, **kwargs)


class InteractiveOptionPage(InteractivePage):
    def execute(self, *args, contracts, **kwargs):
        parameters = dict(contracts=contracts)
        options = self.load(InteractiveDataset.OPTIONS, *args, **parameters, **kwargs)



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



