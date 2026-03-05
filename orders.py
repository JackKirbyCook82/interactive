# -*- coding: utf-8 -*-
"""
Created on Thurs Mar 5 2026
@name:   Interactive Order Objects
@author: Jack Kirby Cook

"""

import pandas as pd

from finance.concepts import Concepts
from webscraping.webpages import WebJSONPage, WebUploader

__author__ = "Jack Kirby Cook"
__all__ = ["InteractiveOrderUploader"]
__copyright__ = "Copyright 2026, Jack Kirby Cook"
__license__ = "MIT License"


class InteractiveOrderPage(WebJSONPage):
    def execute(self, *args, order, **kwargs):
        pass


class InteractiveOrderUploader(WebUploader, page=InteractiveOrderPage):
    def execute(self, prospects, /, **kwargs):
        assert isinstance(prospects, pd.DataFrame)
        if self.empty(prospects): return

    def upload(self, order, /, **kwargs):
        pass

    @staticmethod
    def calculator(prospects, /, term, tenure, **kwargs):
        assert term in (Concepts.Markets.Term.MARKET, Concepts.Markets.Term.LIMIT)



