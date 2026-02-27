# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 2026
@name:   Interactive Brokers Market Objects
@author: Jack Kirby Cook

"""

from webscraping.webpages import WebJSONPage
from webscraping.webdatas import WebJSON
from support.mixins import Emptying, Sizing, Partition, Logging

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = []
__copyright__ = "Copyright 2026, Jack Kirby Cook"
__license__ = "MIT License"


class InteractiveStockPage(WebJSONPage):
    pass

class InteractiveContractPage(WebJSONPage):
    pass

class InteractiveOptionPage(WebJSONPage):
    pass



class InteractiveDownloader(Sizing, Emptying, Partition, Logging, ABC, title="Downloaded"):
    def __init_subclass__(cls, *args, page, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        cls.Page = page

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = self.Page(*args, **kwargs)


class InteractiveSecurityDownloader(InteractiveDownloader):
    pass


class InteractiveStockDownloader(InteractiveDownloader, page=InteractiveStockPage):
    def execute(self, symbols, /, **kwargs):
        pass


class InteractiveOptionDownloader(InteractiveDownloader, page=InteractiveOptionPage):
    def execute(self, contracts, /, **kwargs):
        pass


class InteractiveContractDownloader(InteractiveDownloader, page=InteractiveContractPage):
    def execute(self, symbols, /, **kwargs):
        pass



