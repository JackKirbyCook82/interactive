# -*- coding: utf-8 -*-
"""
Created on Thurs Mar 5 2026
@name:   Interactive Order Objects
@author: Jack Kirby Cook

"""

import numpy as np
import pandas as pd
import ib_insync as ibkr
from abc import ABC

from finance.concepts import Querys, Concepts, Securities
from webscraping.webpages import WebJSONPage, WebUploader
from support.mixins import Naming

__author__ = "Jack Kirby Cook"
__all__ = ["InteractiveOrderUploader"]
__copyright__ = "Copyright 2026, Jack Kirby Cook"
__license__ = "MIT License"


class InteractiveSecurity(Naming, ABC, fields=[]): pass
class InteractiveOption(InteractiveSecurity, fields=[]): pass
class InteractiveStock(InteractiveSecurity): pass
class InteractiveOrder(Naming, fields=[]): pass
class InteractiveValuation(Naming, fields=["npv"]):
    def __str__(self): return f"${self.npv:.0f}"


class InteractiveOrderPage(WebJSONPage):
    def execute(self, *args, order, **kwargs):
        pass


class InteractiveOrderUploader(WebUploader, page=InteractiveOrderPage):
    def execute(self, prospects, /, **kwargs):
        assert isinstance(prospects, pd.DataFrame)
        if self.empty(prospects): return
        for order, valuation in self.calculator(prospects, **kwargs):
            self.upload(order, **kwargs)
            securities = ", ".join(list(map(str, order.securities)))
            self.console(f"{str(securities)}[{order.quantity:.0f}] @ {str(valuation)}")

    def upload(self, order, /, **kwargs):
        assert order.term in (Concepts.Markets.Term.MARKET, Concepts.Markets.Term.LIMIT)
        self.page(order=order, **kwargs)

    @staticmethod
    def calculator(prospects, /, term, tenure, **kwargs):
        assert term in (Concepts.Markets.Term.MARKET, Concepts.Markets.Term.LIMIT)
        for index, prospect in prospects.iterrows():
            strategy, quantity = prospect[["strategy", "quantity"]].values
            spot, breakeven = prospect[["spot", "breakeven"]].values
            settlement = prospect[list(Querys.Settlement)].to_dict()
            options = prospect[list(map(str, Securities.Options))].to_dict()
            options = {Securities.Options[option]: strike for option, strike in options.items() if not np.isnan(strike)}
            stocks = [Securities.Stocks(stock) for stock in strategy.stocks]
            assert spot >= breakeven and quantity >= 1
            options = [InteractiveOption(strike=strike, quantity=quantity * 1, **dict(security), **settlement) for security, strike in options.items()]
            stocks = [InteractiveStock(quantity=quantity * 100, **dict(security), **settlement) for security in stocks]
            order = InteractiveOrder(securities=options + stocks, term=term, tenure=tenure, limit=-breakeven, stop=None, **settlement)
            valuation = InteractiveValuation(npv=prospect["npv"])
            yield order, valuation




